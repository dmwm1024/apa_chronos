from collections import defaultdict
from app.extensions import SessionLocal
from app.models import Division, Schedule, PoolTable
from flask_babel import _
from flask import flash, render_template


class TableWizard:
    def __init__(self):
        self.db = SessionLocal()
        self.output_messages = []

        # Loop over each division, get the Venue from the divisions first match (all matches are at the same venue)
        #       If the division's venue doesn't have any tables yet, Fail.

        for division in self.db.query(Division).all():
            if not division.schedules:
                self.output_messages.append(f"No schedules found for Division ({division.name}).")
                continue

            venue = division.schedules[0].venue

            # Skip any divisions that do not have any tables assigned.
            if len(venue.pooltables) == 0:
                self.output_messages.append(f'Cannot begin Table Assignment for Division ({division.name}) as Venue ({venue.name} has no tables.')
                continue
            else:
                scheduled_matches = []

                # Division Schedules
                schedules = self.db.query(Schedule).filter_by(division_id=division.id).all()

                # Track usage of pool tables across matches (table_id -> team_id -> count)
                table_usage = defaultdict(lambda: defaultdict(int))

                # Track last pool table assignment for each team (team_id -> last_table_id)
                last_pool_table_used = defaultdict(lambda: None)

                for schedule in schedules:
                    venue_id = schedule.venue_id
                    if not venue_id:
                        continue

                    # Get the available pool tables at the venue
                    available_tables = self.db.query(PoolTable).filter_by(venue_id=venue_id).all()

                    # Track which tables have been used for this day's schedule
                    tables_used_today = set()

                    # Schedule represents a match with home_team_id and away_team_id
                    home_team_id = schedule.home_team_id
                    away_team_id = schedule.away_team_id

                    # Sort available tables by the least used for both home and away teams
                    available_tables.sort(key=lambda table: (
                            table_usage[table.id][home_team_id] + table_usage[table.id][away_team_id]))

                    # Assign the first table that hasn't been used today and isn't the last one used by either team
                    assigned_table = None
                    for table in available_tables:
                        if table.id not in tables_used_today and \
                                table.id != last_pool_table_used[home_team_id] and \
                                table.id != last_pool_table_used[away_team_id]:
                            assigned_table = table
                            break

                    if assigned_table:
                        # Assign the pool table to the schedule (match)
                        schedule.pooltable_id = assigned_table.id
                        self.db.add(schedule)

                        # Mark this table as used today
                        tables_used_today.add(assigned_table.id)

                        # Update usage counts and last used tables for both teams
                        table_usage[assigned_table.id][home_team_id] += 1
                        table_usage[assigned_table.id][away_team_id] += 1
                        last_pool_table_used[home_team_id] = assigned_table.id
                        last_pool_table_used[away_team_id] = assigned_table.id
                        self.output_messages.append(f"Completed Table Assignments for Division: {division.name}")

        self.db.commit()

