from flask import Blueprint

bp = Blueprint('index', __name__)

from app.league.index import routes
