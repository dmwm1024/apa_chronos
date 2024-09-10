from app.main import bp
from app.models import Division, Venue, Team
from flask import render_template
from flask_babel import _, lazy_gettext as _l
from app.extensions import SessionLocal


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    db = SessionLocal()
    divisions = db.query(Division).order_by(Division.number).all()
    venues = db.query(Venue).all()
    teams = db.query(Team).all()
    return render_template('main/index.html', divisions=divisions, venues=venues, teams=teams)
