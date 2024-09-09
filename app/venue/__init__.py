from flask import Blueprint

bp = Blueprint('venue', __name__)

from app.division import routes