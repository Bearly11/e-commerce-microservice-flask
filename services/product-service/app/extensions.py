from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()