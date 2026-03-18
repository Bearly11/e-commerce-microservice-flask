from flask import Flask
from .extensions import db, migrate, jwt, mail
from user_config import Config
from .routes.user_route import user_bp
from .services.user_service import UserService
from apscheduler.schedulers.background import BackgroundScheduler

def create_app():
    app = Flask(__name__)
    app .config.from_object(Config)
    #Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)

    #Register blueprints
    app.register_blueprint(user_bp)

    # Schedule expire pending users task
    scheduler = BackgroundScheduler()
    def schedule_expire_pending_users():
        with app.app_context():
            UserService.expire_pending_users()
    scheduler.add_job(schedule_expire_pending_users, 'interval', minutes=1)
    scheduler.start()
    return app