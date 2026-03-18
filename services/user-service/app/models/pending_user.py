from ..extensions import db

class PendingUser(db.Model):
    __tablename__ = 'pending_users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    verification_token = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime,default=db.func.current_timestamp())
    