from ..extensions import db, mail
from flask_mail import Message
from ..models.user import User
from ..models.pending_user import PendingUser
import random
import re
from datetime import datetime, timedelta

from ..models.refresh_token import RefreshToken


class UserService:
    @staticmethod
    def get_all_users():
        return User.query.all()

    @staticmethod
    def create_user(name, email, password_hash):
        new_user = User(name=name, email=email, password_hash=password_hash)
        db.session.add(new_user)
        db.session.commit()
        return new_user

    @staticmethod
    def get_user_by_id(user_id):
        return User.query.get(user_id)

    @staticmethod
    def get_user_by_email(email):
        return User.query.filter_by(email=email).first()

    @staticmethod
    def update_user(user_id, name=None, email=None, password_hash=None):
        user = UserService.get_user_by_id(user_id)
        if not user:
            return None
        if name:
            user.name = name
        if email:
            user.email = email
        if password_hash:
            user.password_hash = password_hash
        db.session.commit()
        return user

    @staticmethod
    def delete_user(user_id):
        user = UserService.get_user_by_id(user_id)
        if not user:
            return False
        db.session.delete(user)
        db.session.commit()
        return True

    @staticmethod
    def reset_password(user_id, new_password_hash):
        user = UserService.get_user_by_id(user_id)
        if not user:
            return None
        user.password_hash = new_password_hash
        db.session.commit()
        return user

    #########################
    # Pending user management
    ##########################

    @staticmethod
    def get_pending_user_by_email(email):
        return PendingUser.query.filter_by(email=email).first()

    @staticmethod
    def create_pending_user(name, email, password_hash):

        verification_token = str(random.randint(100000, 999999))
        exiting_email =PendingUser.query.filter_by(email=email).first()
        if exiting_email:
            db.session.delete(exiting_email)
            db.session.commit()
        new_pending_user = PendingUser(name=name, email=email, password_hash=password_hash,
                                       verification_token=verification_token)
        db.session.add(new_pending_user)
        db.session.commit()
        return new_pending_user

    @staticmethod
    def get_token_by_email(email):
        pending_user = PendingUser.query.filter_by(email=email).first()
        if pending_user:
            return pending_user.verification_token
        return None

    #Validate password strength using regex
    @staticmethod
    def is_strong_password(password):
        password_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
        return re.match(password_regex, password) is not None

    #Validate email format using regex
    @staticmethod
    def is_valid_email(email):
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_regex, email) is not None

    @staticmethod
    def two_factor_authenticate(email, token):
        pending_user = PendingUser.query.filter_by(email=email).first()
        if not pending_user:
            return None

        if pending_user.verification_token != token:
            return None

        new_user = UserService.create_user(
            name=pending_user.name,
            email=pending_user.email,
            password_hash=pending_user.password_hash
        )
        db.session.delete(pending_user)
        db.session.commit()
        return new_user

    @staticmethod
    def expire_pending_users():
        expired_time = datetime.utcnow() - timedelta(minutes=10)
        expired_users = PendingUser.query.filter(PendingUser.created_at < expired_time).all()
        for pending_user in expired_users:
            db.session.delete(pending_user)
        db.session.commit()

    #########################
    # Send verification email
    ##########################
    @staticmethod
    def send_verification_email(email, token):
        msg = Message(
            subject="Email Verification Code",
            recipients=[email],
        )

        msg.body=f"""
        Hello,
        Your verification code is:
        
        {token}
        
        This code will expire in 10 minutes.
        """
        mail.send(msg)

    ###################
    # refresh token management
    ###################


    @staticmethod
    def create_refresh_token(user_id, jti, expires_in=7):

        expires_at = datetime.utcnow() + timedelta(days=expires_in)
        refresh_token = RefreshToken(user_id=user_id, jti=jti, expires_at=expires_at)
        db.session.add(refresh_token)
        db.session.commit()
        return refresh_token

    @staticmethod
    def revoke_refresh_token(user_id,jti):

        refresh_token = RefreshToken.query.filter_by(
            user_id=user_id,
            jti=jti,
            is_revoked=False).first()
        if refresh_token:
            refresh_token.is_revoked = True
            db.session.commit()
            return True
        return False

    @staticmethod
    def is_refresh_token_valid(user_id,jti):
        stored = RefreshToken.query.filter_by(
            user_id=user_id,
            jti=jti,
            is_revoked=False
        ).first()
        if not stored:
            return False
        if stored.expires_at < datetime.utcnow():
            stored.is_revoked = True
            db.session.commit()
            return False
        return True











