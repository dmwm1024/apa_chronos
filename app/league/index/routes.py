from app.league.index import bp
from flask import render_template, redirect, url_for
from app.services.LeagueAPI import LeagueAPI


@bp.route('/', methods=['GET', 'POST'])
def reroute():
    return redirect('/jacksonville')


@bp.route('/<string:Slug>', methods=['GET', 'POST'])
@bp.route('/index/<string:Slug>', methods=['GET', 'POST'])
def index(Slug):
    api = LeagueAPI("https://gql.poolplayers.com/graphql")
    league = api.query_league(slug=Slug)

    return render_template('league/index/index.html', league=league)
