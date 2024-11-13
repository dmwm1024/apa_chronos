from flask import render_template, redirect, url_for, flash
from app.league.divisionPair import bp
from app.services.LeagueAPI import LeagueAPI
from app.league.divisionPair.forms import DivisionPairForm
from app.models import DivisionPair, MatchHistory
from app import db
from flask_login import login_required
import logging
from app.services.TableWizard import reassign_tables_for_division_pair


@bp.route('/divisionPair/', defaults={'DivisionPair_ID': None})
@bp.route('/divisionPair/<int:DivisionPair_ID>', methods=['GET', 'POST'])
@login_required
def index(DivisionPair_ID):
    pairs = DivisionPair.query.all()
    form = DivisionPairForm()

    return render_template('league/divisionPair/index.html', form=form, DivisionPair_ID=DivisionPair_ID, pairs=pairs)


@bp.route('/divisionPair/reassignTables/<int:DivisionPair_ID>', methods=['GET', 'POST'])
@login_required
def reassignTables(DivisionPair_ID):
    reassign_tables_for_division_pair(DivisionPair_ID)

    return redirect(url_for('divisionPair.matches', DivisionPair_ID=DivisionPair_ID))


@bp.route('/divisionPair/matches/<int:DivisionPair_ID>', methods=['GET', 'POST'])
@login_required
def matches(DivisionPair_ID):
    api = LeagueAPI("https://gql.poolplayers.com/graphql")
    league = api.query_league(slug='jacksonville')
    pair = DivisionPair.query.get(DivisionPair_ID)

    division_a_check = False
    division_b_check = False

    if pair.division_B == '':
        division_b_check = True

    division_a = None
    division_b = None

    # Fetch Divisions
    divisions = api.query_divisions(slug='jacksonville', session_id=league['data']['league']['currentSessionId'])

    for division in divisions['data']['league']['divisions']:
        if division['number'] == pair.division_A:
            division_a = division
            division_a_check = True
        if pair.division_B is not '' and division['number'] == pair.division_B:
            division_b = division
            division_b_check = True
        if division_a_check and division_b_check:
            break

    schedule_a = api.query_division_schedule(division_a['id']) if division_a else []
    schedule_b = api.query_division_schedule(division_b['id']) if division_b else []

    # Collect all match IDs from both schedules to retrieve assigned tables
    match_ids = [
        match['id'] for week in schedule_a['data']['division']['schedule'] for match in week['matches']
    ]
    if schedule_b:
        match_ids.extend([
            match['id'] for week in schedule_b['data']['division']['schedule'] for match in week['matches']
        ])

    # Retrieve table assignments from MatchHistory for the collected match IDs
    match_history_entries = MatchHistory.query.filter(MatchHistory.match_ID.in_(match_ids)).all()
    table_assignments = {entry.match_ID: entry.table_number for entry in match_history_entries}

    return render_template('league/divisionPair/matches.html', division_a=division_a, division_b=division_b,
                           schedule_a=schedule_a, schedule_b=schedule_b, DivisionPair_ID=DivisionPair_ID,
                           pair=pair, table_assignments=table_assignments)


@bp.route('/divisionPair/create', methods=['GET', 'POST'])
@login_required
def create_DivisionPair():
    form = DivisionPairForm()

    if form.validate_on_submit():
        new_pair = DivisionPair(
            division_A=form.division_a.data,
            division_B=form.division_b.data,
            location=form.location.data,
            weeknight=form.weeknight.data,
            table_string=form.table_string.data
        )

        db.session.add(new_pair)
        db.session.commit()

        return redirect(url_for('divisionPair.index'))

    return render_template('league/divisionPair/create.html', form=form)


@bp.route('/divisionPair/delete/<int:DivisionPair_ID>', methods=['GET', 'POST'])
@login_required
def delete_divisionPair(DivisionPair_ID):
    pair = DivisionPair.query.get(DivisionPair_ID)
    if pair:
        db.session.delete(pair)
        db.session.commit()
        return redirect(url_for('divisionPair.index'))


@bp.route('/divisionPair/edit/<int:DivisionPair_ID>', methods=['GET', 'POST'])
@login_required
def edit_divisionPair(DivisionPair_ID):
    form = DivisionPairForm()
    pair = DivisionPair.query.get(DivisionPair_ID)

    if form.validate_on_submit():

        pair = DivisionPair.query.get(DivisionPair_ID)
        pair.division_A = form.division_a.data,
        pair.division_B = form.division_b.data,
        pair.location = form.location.data,
        pair.weeknight = form.weeknight.data,
        pair.table_string = form.table_string.data

        db.session.commit()
        return redirect(url_for('divisionPair.index'))

    else:
        form.id = pair.id
        form.division_a.data = pair.division_A
        form.division_b.data = pair.division_B
        form.location.data = pair.location
        form.weeknight.data = pair.weeknight
        form.table_string.data = pair.table_string

    return render_template('league/divisionPair/edit.html', form=form)


