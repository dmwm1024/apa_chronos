from collections import defaultdict
from app.extensions import SessionLocal
from app.models import Division, Schedule, PoolTable
from flask_babel import _
from flask import flash, render_template


class TableWizard:
    def __init__(self):
        self.db = SessionLocal()
        self.output_messages = []
        self.assign_pool_tables()

    def assign_pool_tables(self):
        """
        Assign PoolTables to each Schedule match based on the defined goals.
        Ensure no two teams are assigned the same table on the same date.
        """
        # Track pool table usage (team_id -> pooltable_id -> count)
        table_usage = defaultdict(lambda: defaultdict(int))

        # Track last pool table assignment for each team (team_id -> last_pool_table_id)
        last_pool_table_used = defaultdict(lambda: None)

        # Track which tables are used on a specific date (venue_id -> date -> set of pooltable_ids)
        tables_used_on_date = defaultdict(lambda: defaultdict(set))

        # Track teams playing across divisions on the same night using team name
        team_schedule_by_name = defaultdict(list)

        # Gather team information across divisions
        for division in self.db.query(Division).all():
            for schedule in division.schedules:
                if schedule.venue and schedule.date:
                    home_team_id = schedule.home_team_id
                    away_team_id = schedule.away_team_id
                    home_team_name = schedule.home_team.name
                    away_team_name = schedule.away_team.name
                    schedule_date = schedule.date

                    # Track team schedules by team name and schedule date
                    team_schedule_by_name[(home_team_name, schedule_date)].append((home_team_id, schedule))
                    team_schedule_by_name[(away_team_name, schedule_date)].append((away_team_id, schedule))

        # Process each division for table assignment
        for division in self.db.query(Division).all():
            if not division.schedules:
                self.output_messages.append(f"No schedules found for Division ({division.name}).")
                continue

            # Process matches in the division
            for schedule in division.schedules:
                venue = schedule.venue
                if not venue or not venue.pooltables:
                    self.output_messages.append(f"No available PoolTables for Division ({division.name}) at Venue ({venue.name})")
                    continue

                # Get available PoolTables for the venue, sorted by their number (assuming the name is numeric)
                available_tables = sorted(venue.pooltables, key=lambda table: int(table.name))

                # Get team names and IDs and the match date
                home_team_name = schedule.home_team.name
                away_team_name = schedule.away_team.name
                home_team_id = schedule.home_team_id
                away_team_id = schedule.away_team_id
                schedule_date = schedule.date

                # Check if teams are playing more than one match on the same night (in different divisions)
                home_team_multiple_matches = len([s for t_id, s in team_schedule_by_name[(home_team_name, schedule_date)] if t_id != home_team_id]) > 0
                away_team_multiple_matches = len([s for t_id, s in team_schedule_by_name[(away_team_name, schedule_date)] if t_id != away_team_id]) > 0

                # Prioritize nearby tables for teams with the same name but different team IDs
                if home_team_multiple_matches or away_team_multiple_matches:
                    assigned_table = self.assign_nearby_table(available_tables, home_team_id, away_team_id, last_pool_table_used, tables_used_on_date, venue.id, schedule_date)
                else:
                    # Assign based on the least-used table that hasn't been used in the last match and isn't used on this date
                    assigned_table = self.assign_least_used_table(available_tables, home_team_id, away_team_id, table_usage, last_pool_table_used, tables_used_on_date, venue.id, schedule_date)

                if assigned_table:
                    # Assign the selected table to the schedule match
                    schedule.pooltable_id = assigned_table.id
                    self.db.add(schedule)

                    # Update table usage and last used tables for both teams
                    table_usage[home_team_id][assigned_table.id] += 1
                    table_usage[away_team_id][assigned_table.id] += 1
                    last_pool_table_used[home_team_id] = assigned_table.id
                    last_pool_table_used[away_team_id] = assigned_table.id

                    # Mark this table as used for this date
                    tables_used_on_date[venue.id][schedule_date].add(assigned_table.id)

                    self.output_messages.append(f"{schedule.home_team.name} vs. {schedule.away_team.name} assigned to PoolTable {assigned_table.name} at {venue.name}")

        self.db.commit()

    def assign_nearby_table(self, available_tables, home_team_id, away_team_id, last_pool_table_used, tables_used_on_date, venue_id, schedule_date):
        """
        Assign the nearest available table based on team IDs and last used table.
        Teams with the same name playing on the same night in different divisions should be on nearby tables.
        Ensure no two teams are assigned the same table on the same date.
        """
        available_tables.sort(key=lambda table: int(table.name))  # Assume table names are numeric for proximity sorting

        # Ensure unique team IDs get different tables, even for teams with the same name
        for table in available_tables:
            if table.id != last_pool_table_used[home_team_id] and \
               table.id != last_pool_table_used[away_team_id] and \
               table.id not in tables_used_on_date[venue_id][schedule_date]:  # Ensure table isn't already used on this date
                return table

        return None  # No available nearby table found

    def assign_least_used_table(self, available_tables, home_team_id, away_team_id, table_usage, last_pool_table_used, tables_used_on_date, venue_id, schedule_date):
        """
        Assign the table that has been used the least by both the home and away teams, avoiding their last used table.
        Ensure no two teams are assigned the same table on the same date.
        """
        # Sort tables by least used, but ensure they didn't use this table last match and it hasn't been used on the same date
        available_tables.sort(key=lambda table: (
            table_usage[home_team_id][table.id] + table_usage[away_team_id][table.id]
        ))

        # Assign the first table that hasn't been used in the last match and isn't already used on this date
        for table in available_tables:
            if table.id != last_pool_table_used[home_team_id] and \
               table.id != last_pool_table_used[away_team_id] and \
               table.id not in tables_used_on_date[venue_id][schedule_date]:  # Ensure table isn't already used on this date
                return table

        return None  # No table available that satisfies the condition
