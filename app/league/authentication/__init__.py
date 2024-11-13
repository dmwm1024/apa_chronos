from flask import Blueprint

bp = Blueprint('authentication', __name__)

from app.league.authentication import routes