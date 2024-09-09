from flask import Blueprint

bp = Blueprint('division', __name__)

from app.division import routes