from app.league.index import bp
from app.models import User, MatchHistory, DivisionPair
from flask import render_template, redirect, url_for, request
from werkzeug.security import check_password_hash
from app.services.LeagueAPI import LeagueAPI


@bp.route('/', methods=['GET', 'POST'])
def reroute():
    return redirect('/jacksonville')


@bp.route('/<string:Slug>', methods=['GET', 'POST'])
@bp.route('/index/<string:Slug>', methods=['GET', 'POST'])
def index(Slug):
    api = LeagueAPI("https://gql.poolplayers.com/graphql")
    league = api.query_league(slug=Slug)
    pairs = DivisionPair.query.all()

    return render_template('league/index/index.html', league=league, pairs=pairs)


@bp.route('/index/matches/<int:DivisionPair_ID>', methods=['GET', 'POST'])
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

    return render_template('league/index/matches.html', division_a=division_a, division_b=division_b,
                           schedule_a=schedule_a, schedule_b=schedule_b, DivisionPair_ID=DivisionPair_ID,
                           pair=pair, table_assignments=table_assignments)
