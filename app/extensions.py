from config import Config
from sqlalchemy import MetaData
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_babel import Babel


metadata = MetaData(naming_convention=Config.SQLALCHEMY_CONVENTION)
db = SQLAlchemy(metadata=metadata)
migrate = Migrate(render_as_batch=True)
babel = Babel()
