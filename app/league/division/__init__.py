from flask import Blueprint

bp = Blueprint('division', __name__)

from app.league.division import routes