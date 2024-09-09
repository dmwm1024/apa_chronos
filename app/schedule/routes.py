from flask import render_template, request, flash, redirect, url_for
from flask_babel import _

from app.schedule import bp
from app.schedule.forms import FileUpload
from app.services.helpers import ScheduleExtractor, Schedule
from app.models import Division, Team, Match
from app.extensions import db

from datetime import datetime

from collections import defaultdict

import random


@bp.route('/schedule', methods=['GET', 'POST'])
def index():
    form = FileUpload()

    if request.method == 'POST':
        files = request.files.getlist("file")
        schedules = []
        division = {}

        # ANALYSIS
        for file in files:
            schedule = Schedule(file)
            schedules.append(schedule)
            last_table_used = defaultdict(lambda: None)

            # Data Integrity
            if Division_Exists(schedule.division_number):
                division = Division.query.filter_by(Division_Number=schedule.division_number).first()
                All_Teams = ValidateTeams(schedule, division)

                # Assign Tables
                pooltables = division.Venue_rel.pooltables
                if len(pooltables) == 0:
                    flash(_('You must first create the tables for this venue.'))
                    error = 'You must first create the tables for this venue.'
                    print('Here 1')
                    return render_template('schedule/index.html', title='Scheduler', form=form, error=error)

                scheduled_matches = AssignTables(division, schedule, pooltables, All_Teams)

                CreateMatches(scheduled_matches)

                # AssignTables(division, schedule.matchups)

            # Division does not exist. Terminate.
            else:
                print('Division not found.')
                flash('You must first create this division (Division Number: ' + schedule.division_number + ')')
                error = 'You must first create this division (Division Number: ' + schedule.division_number + ')'
                print('Here 2')
                return render_template('schedule/index.html', title='Scheduler', form=FileUpload(), error=error)

        print('going main')
        print('Here 3')
        return redirect(url_for('main.index'))

    print('Here 4')
    return render_template('schedule/index.html', title='Scheduler', form=form)


def CreateMatches(scheduled_matches):
    # def Match_Exists(Division_ID, Venue_ID, Match_PlayDate, HomeTeam_ID, AwayTeam_ID)
    for match in scheduled_matches:

        check = Match_Exists(match.Division, match.Venue, match.Match_PlayDate, match.HomeTeam, match.AwayTeam)
        if not check:
            match.Match_PlayDate = datetime.strptime(match.Match_PlayDate, "%m/%d/%Y").date()
            db.session.add(match)

    db.session.commit()
    return scheduled_matches


def AssignTables(division, schedule, tables, All_Teams):
    if len(tables) == 0:
        flash(_('You must first create the tables for this venue.'))
        return False

    scheduled_matches = []

    # Dictionary to track how many times each team has played on each table
    table_usage_count = defaultdict(lambda: defaultdict(int))  # {team_id: {table_id: count}}

    # Dictionary to track the last table used by each team within the same method scope
    last_table_used = {}  # {team_id: table_id}

    for week in schedule.matchups:
        assigned_tables = []

        for match in week['matchups']:
            print('Home Team: ' + match['home_team'] + ' - Away Team: ' + match['away_team'])

            home_team = GetTeamFromTeams(division, match['home_team'], All_Teams)
            away_team = GetTeamFromTeams(division, match['away_team'], All_Teams)

            if not home_team or not away_team:
                continue

            # Get the last table used by both teams (if they played last week)
            last_home_team_table = last_table_used.get(home_team.Team_ID)
            last_away_team_table = last_table_used.get(away_team.Team_ID)

            # Sort tables by the least number of times both teams have played on them
            table_scores = []
            for table in tables:
                # Get the count of times both teams played on this table
                home_team_table_usage = table_usage_count[home_team.Team_ID].get(table.PoolTable_ID, 0)
                away_team_table_usage = table_usage_count[away_team.Team_ID].get(table.PoolTable_ID, 0)

                # Add up the total usage for both teams
                combined_usage = home_team_table_usage + away_team_table_usage

                # Ensure the table hasn't already been assigned this week and is not the same as last week's table
                if table not in assigned_tables and table.PoolTable_ID != last_home_team_table and table.PoolTable_ID != last_away_team_table:
                    table_scores.append((table, combined_usage))

            # If no tables are available after excluding last week's tables, allow tables with prior usage
            if not table_scores:
                table_scores = [
                    (table, combined_usage) for table in tables
                    if table not in assigned_tables
                ]

            # Sort tables by the least usage count for both teams
            sorted_tables = sorted(table_scores, key=lambda x: x[1])

            # Select the table with the least usage (first in the sorted list)
            assigned_table = sorted_tables[0][0]

            # Add the assigned table to the list of tables assigned this week
            assigned_tables.append(assigned_table)

            # Update the table usage count for both teams
            table_usage_count[home_team.Team_ID][assigned_table.PoolTable_ID] += 1
            table_usage_count[away_team.Team_ID][assigned_table.PoolTable_ID] += 1

            # Update the last table used by both teams
            last_table_used[home_team.Team_ID] = assigned_table.PoolTable_ID
            last_table_used[away_team.Team_ID] = assigned_table.PoolTable_ID

            new_match = Match(Match_WeekNum=week['week'],
                              Match_PlayDate=week['date'],
                              Division=division.Division_ID,
                              HomeTeam=home_team.Team_ID,
                              AwayTeam=away_team.Team_ID,
                              Venue=division.Venue_rel.Venue_ID,
                              PoolTable=assigned_table.PoolTable_ID)

            scheduled_matches.append(new_match)

    return scheduled_matches


def GetTeamFromTeams(division, Team_Number, All_Teams):
    if len(Team_Number) == 1:
        Team_Number = '0' + Team_Number

    Team_Number = division.Division_Number + Team_Number
    team = Team.query.filter_by(Team_Number=Team_Number).first()

    if team:
        return team
    else:
        return False


def ValidateTeams(schedule, division):
    teams = []

    for team in schedule.teams:
        teams.append(Team_CreateIfNotExist(division, team['Team Number'], team['Team Name']))

    return teams


def Division_Exists(Division_Number):
    division = Division.query.filter_by(Division_Number=Division_Number).first()
    if hasattr(division, 'Division_ID'):
        return division
    return False


def Match_Exists(Division_ID, Venue_ID, Match_PlayDate, HomeTeam_ID, AwayTeam_ID):
    match = Match.query.filter_by(Division=Division_ID, Venue=Venue_ID,
                                  Match_PlayDate=Match_PlayDate, HomeTeam=HomeTeam_ID,
                                  AwayTeam=AwayTeam_ID).first()
    if match:
        return match
    else:
        return False


def Team_CreateIfNotExist(Division_Instance, Team_Number, Team_Name):
    team = Team.query.filter_by(Team_Number=Team_Number).first()
    if team:
        return team
    else:
        flash('Team (' + Team_Name + ') created within ' + Division_Instance.Division_Name)
        team = Team(Team_Number=Team_Number, Team_Name=Team_Name, Division=Division_Instance.Division_ID)
        db.session.add(team)
        db.session.commit()
        return team
