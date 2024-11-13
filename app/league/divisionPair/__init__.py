from flask import Blueprint

bp = Blueprint('divisionPair', __name__)

from app.league.divisionPair import routes