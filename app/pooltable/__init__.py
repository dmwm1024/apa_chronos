from flask import Blueprint

bp = Blueprint('pooltable', __name__)

from app.pooltable import routes