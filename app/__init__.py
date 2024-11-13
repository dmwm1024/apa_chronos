from flask import Flask
from flask_migrate import Migrate
from config import Config
from .extensions import db
from .models import DivisionPair, MatchHistory
import logging

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.logger.setLevel(logging.INFO)

    # Init Extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    with app.app_context():

        db.create_all()

    # Init Routing

    # Index
    from app.league.index.routes import bp as index_bp
    app.register_blueprint(index_bp)

    # Divisions
    from app.league.division.routes import bp as division_bp
    app.register_blueprint(division_bp)

    # Division Pairs
    from app.league.divisionPair.routes import bp as divisionPair_bp
    app.register_blueprint(divisionPair_bp)

    return app
