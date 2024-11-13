from flask import render_template
from app.league.division import bp
from app.services.LeagueAPI import LeagueAPI


@bp.route('/division/<int:Division_ID>', methods=['GET', 'POST'])
def index(Division_ID):
    api = LeagueAPI("https://gql.poolplayers.com/graphql")
    division = api.query_division(Division_ID)
    schedule = api.query_division_schedule(Division_ID)

    return render_template('league/division/index.html', division=division, schedule=schedule, Division_ID=Division_ID)