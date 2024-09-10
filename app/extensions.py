from flask_babel import Babel
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, create_engine, inspect
from sqlalchemy.orm import sessionmaker
from app.models import Base
import os

from config import Config

metadata = MetaData(naming_convention=Config.SQLALCHEMY_CONVENTION)
db = SQLAlchemy(metadata=metadata)
migrate = Migrate(render_as_batch=True)
babel = Babel()

basedir = os.path.abspath(os.path.dirname(__file__))
engine = create_engine(f"sqlite:///{os.path.join(basedir, 'league_data.db')}")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
inspector = inspect(engine)

existing_tables = inspector.get_table_names()
if not existing_tables:
    print('Database has not been initialized. Initializing Database...')
    Base.metadata.create_all(engine)
    print('Database successfully initialized.')
else:
    print('Using existing database.')
