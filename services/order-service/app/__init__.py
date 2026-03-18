from flask import Flask
from order_config import Config
from .extensions import db, migrate
from .routes.order_route import order_bp
from .services.order_service import expire_orders
from apscheduler.schedulers.background import BackgroundScheduler


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Import and register blueprints
    app.register_blueprint(order_bp)

    # Schedule order expiration task
    scheduler = BackgroundScheduler()
    def schedule_expire_orders():
        with app.app_context():
            expire_orders()
    scheduler.add_job(schedule_expire_orders, 'interval', minutes=1)
    scheduler.start()

    return app