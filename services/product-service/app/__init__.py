from flask import Flask
from config import Config
from .extensions import db, migrate
from .routes.product_routes import product_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    app.register_blueprint(product_bp)

    return app

