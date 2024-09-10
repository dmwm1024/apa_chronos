from flask import Flask, request, current_app
from app import models
from .extensions import db, migrate, babel, engine
from config import Config
from sqlalchemy.orm import sessionmaker
from flask_babel import Babel, lazy_gettext as _l


def get_locale():
    return request.accept_languages.best_match(current_app.config['LANGUAGES'])


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    babel.init_app(app, locale_selector=get_locale)

    # Register Blueprints
    from app.errors import bp as errors_blueprint
    app.register_blueprint(errors_blueprint)

    from app.main.routes import bp as main_bp
    app.register_blueprint(main_bp)

    from app.division.routes import bp as division_bp
    app.register_blueprint(division_bp)

    from app.venue.routes import bp as venue_bp
    app.register_blueprint(venue_bp)

    from app.team.routes import bp as team_bp
    app.register_blueprint(team_bp)

    from app.pooltable.routes import bp as pooltable_bp
    app.register_blueprint(pooltable_bp)

    from app.schedule.routes import bp as schedule_bp
    app.register_blueprint(schedule_bp)

    from app.testing.routes import bp as testing_bp
    app.register_blueprint(testing_bp)

    return app
