from app import db
from app.models import DivisionPair, MatchHistory
from app.services.LeagueAPI import LeagueAPI
from datetime import datetime
import logging

logging.getLogger().setLevel(logging.INFO)

# Greedy Heuristic based Algorithm for Table Assignment


def wipe_match_history_for_division_pair(division_pair_id):
    """Erase all MatchHistory records for a given division pair."""

    # Retrieve the division pair from the database
    division_pair = DivisionPair.query.get(division_pair_id)
    if not division_pair:
        logging.error("No division pair found with ID %s", division_pair_id)
        return f"No division pair found with ID {division_pair_id}"

    # Filter MatchHistory records by the divisions in the division pair
    match_history_to_delete = MatchHistory.query.filter(
        MatchHistory.division_ID.in_([division_pair.division_A, division_pair.division_B])
    ).all()

    # Delete the matched records
    if match_history_to_delete:
        for record in match_history_to_delete:
            db.session.delete(record)
        db.session.commit()
        logging.info("Deleted %d MatchHistory records for division pair ID %s", len(match_history_to_delete),
                     division_pair_id)
        return f"Deleted {len(match_history_to_delete)} MatchHistory records for division pair ID {division_pair_id}"
    else:
        logging.info("No MatchHistory records found for division pair ID %s", division_pair_id)
        return f"No MatchHistory records found for division pair ID {division_pair_id}"


def parse_table_string(table_string):
    """Parse the table string into paired and individual tables."""
    paired_tables = []
    individual_tables = []
    for item in table_string.split(','):
        if '+' in item:
            paired_tables.append(item.split('+'))
        else:
            individual_tables.append(item)
    return paired_tables, individual_tables


def reassign_tables_for_division_pair(division_pair_id):
    # Wipe previous assignments.
    wipe_match_history_for_division_pair(division_pair_id)

    """Reassign tables to matches for a given division pair using the specified assignment strategy."""
    api = LeagueAPI("https://gql.poolplayers.com/graphql")

    # Fetch the division pair from the database
    division_pair = DivisionPair.query.get(division_pair_id)
    if not division_pair:
        logging.error("No division pair found with ID %s", division_pair_id)
        return f"No division pair found with ID {division_pair_id}"

    # Parse available tables and pairs
    paired_tables, individual_tables = parse_table_string(division_pair.table_string)
    original_tables = set(sum(paired_tables, individual_tables))  # Set of all unique tables
    logging.info("Parsed tables: %s and paired tables: %s", individual_tables, paired_tables)

    # Retrieve the division IDs related to this pair
    league = api.query_league(slug='jacksonville')
    session_id = league['data']['league']['currentSessionId']
    divisions = api.query_divisions(slug='jacksonville', session_id=session_id)

    # Collect division IDs that match the division pair numbers
    division_ids = [
        division['id'] for division in divisions['data']['league']['divisions']
        if division['number'] in [division_pair.division_A, division_pair.division_B]
    ]

    # Retrieve matches for the divisions, sorted by date and excluding "Bye" matches
    matches = []
    for division_id in division_ids:
        schedule_data = api.query_division_schedule(division_id)
        for week in schedule_data['data']['division']['schedule']:
            for match in week['matches']:
                if not match['isBye'] and match['home']['name'] != "Bye" and match['away']['name'] != "Bye":
                    matches.append({
                        'id': match['id'],
                        'date': datetime.strptime(week['date'][:10], "%Y-%m-%d"),
                        'weekOfPlay': week['weekOfPlay'],
                        'home': match['home'],
                        'away': match['away'],
                        'division_id': division_id
                    })

    # Sort matches by date
    matches.sort(key=lambda x: x['date'])

    # Organize matches by date and identify teams playing in both divisions
    matches_by_date = {}
    team_matches_per_date = {}
    for match in matches:
        match_date = match['date']
        matches_by_date.setdefault(match_date, []).append(match)

        # Track matches by team to identify teams playing twice on the same night
        home_team_name = match['home']['name']
        team_matches_per_date.setdefault((match_date, home_team_name), []).append(match)

    # Track the last assigned table for each team to avoid repeats
    last_table_assigned = {}
    table_assignment = {}

    # Step 1: Assign paired tables for teams playing twice on the same night
    for match_date, nightly_matches in matches_by_date.items():
        # Reset all available tables at the start of each night
        available_tables = original_tables.copy()

        # Process teams playing twice on the same night
        for (date, team_name), team_matches in team_matches_per_date.items():
            if date == match_date and len(team_matches) == 2:
                # Find an available pair of tables
                for pair in paired_tables:
                    if all(table in available_tables for table in pair):
                        # Assign one table of the pair to each of the two matches
                        table_assignment[team_matches[0]['id']] = pair[0]
                        table_assignment[team_matches[1]['id']] = pair[1]

                        # Update last assigned table for tracking
                        last_table_assigned[team_name] = pair[1]

                        # Remove these tables from available tables for the night
                        available_tables.discard(pair[0])
                        available_tables.discard(pair[1])
                        logging.info("Assigned paired tables %s to team %s for matches on %s", pair, team_name,
                                     match_date)
                        break  # Move to the next team once a pair is assigned

        # Step 2: Assign remaining tables for other matches
        for match in nightly_matches:
            if match['id'] not in table_assignment:  # Skip already assigned matches
                home_team = match['home']['name']
                away_team = match['away']['name']

                # Assign a table that avoids repeat usage by the same team from the last week
                assigned_table = next(
                    (table for table in available_tables),
                    None
                )

                if assigned_table:
                    table_assignment[match['id']] = assigned_table
                    last_table_assigned[home_team] = assigned_table
                    last_table_assigned[away_team] = assigned_table
                    available_tables.remove(assigned_table)
                    logging.info("Assigned table %s for match %s on %s between %s and %s", assigned_table, match['id'], match_date, home_team, away_team)
                else:
                    logging.warning("Not enough tables for all matches on %s", match_date)

    # Step 3: Log assignments in MatchHistory
    match_history_entries = [
        MatchHistory(
            match_ID=match['id'],
            weekOfPlay=match['weekOfPlay'],
            homeTeam_ID=match['home']['id'],
            homeTeam_Name=match['home']['name'],
            awayTeam_ID=match['away']['id'],
            awayTeam_Name=match['away']['name'],
            table_number=table_assignment.get(match['id']),
            division_ID=match['division_id']
        ) for match in matches if match['id'] in table_assignment
    ]

    db.session.bulk_save_objects(match_history_entries)
    db.session.commit()
    logging.info("Table assignments completed and logged in MatchHistory.")
    return "Table assignments completed and logged in MatchHistory."
