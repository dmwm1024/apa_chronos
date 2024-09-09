from app.main import bp
from app.models import Division, Venue, Team, Match
from flask import render_template
from flask_babel import _, lazy_gettext as _l


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    divisions = Division.query.all()
    venues = Venue.query.all()
    teams = Team.query.all()
    return render_template('main/index.html', divisions=divisions, venues=venues, teams=teams)
