from flask_login import UserMixin, login_user, login_required
from sqlalchemy import CheckConstraint, func
from sqlalchemy.exc import IntegrityError
from datetime import timedelta
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from .db import db, bcrypt
from flask import jsonify
from datetime import datetime, timezone, timedelta

class User(UserMixin, db.Model):
    __tablename__ = 'users'
 
    local_time = datetime.now(timezone.utc)
    # table columns
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=local_time, nullable=False)
    bio = db.Column(db.String(200), default='', nullable=True)
    avatar_url = db.Column(db.String(255), default='', nullable=True)

    # table relationships
    favorites = db.relationship('Favorite', back_populates='user')
    posts = db.relationship('Post', back_populates='user')
    likes = db.relationship('PostLike', back_populates='user')
    comments = db.relationship('Comment', back_populates='user')
    notifications_sent = db.relationship('Notification', back_populates='sender', primaryjoin='User.id == Notification.sender_id')
    notifications_received = db.relationship('Notification', back_populates='recipient', primaryjoin='User.id == Notification.recipient_id')

    # database constraints
    __table_args__ = (
            CheckConstraint("length(password_hash) >= 8", name="password_length_check"),
            CheckConstraint("username ~ '^[a-zA-Z0-9_]{1,64}$'", name="handle_constraint"),
            CheckConstraint(func.char_length(username) >= 4, name="min_username_length_constraint"),
    )

    def user_info(self, user_id):
        user = User.query.filter_by(id=user_id).first()
        if user:
            return user.username
        else:
            return None

    @staticmethod
    def get_user_info(username):
        user = User.query.filter_by(username=username).first()
        if user:
            return True, {
                    'username': user.username,
                    'posts': [post.to_dict() for post in user.posts],
                    'reposts': [repost.to_dict() for repost in user.reposts],
                    'bio': user.bio,
                    'avatar_url': user.avatar_url,
                    'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'favorites': [favorite.to_dict() for favorite in user.favorites]
            }
        else:
            return False

    # Authentication functions
    def set_password(self, password):
        pwhash = bcrypt.generate_password_hash(password)
        self.password_hash = pwhash.decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    @staticmethod
    def login_user(username, password):
        if not username or not password:
            return False, 'All fields must be filled out'
        
        user = User.query.filter_by(username=username).first()
        if not user:
            return False, 'User not found'
        if not user.check_password(password):
            return False, 'Incorrect password'
        else:
            user_data = user.to_dict()
            return True, user_data

    # Register User
    @staticmethod
    def register_user(username, password):
        try:
            user = User(username=username)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            return True, user
        except IntegrityError as e:
            db.session.rollback()
            error_info = str(e.orig)
            print(error_info)
            error_messages = {
                    "unique constraint": "Username is already taken. Please choose another one.",
                    "password_length_check": "Password must be at least 8 characters long.",
                    "handle_constraint": "Username can only contain letters, numbers, and underscores.",
                    "min_username_length_constraint": "Username must be at least 4 characters long.",
            }
            
            for error_key, user_message in error_messages.items():
                if error_key in error_info:
                    return False, user_message
            
            return False, 'Unknown error occcured. Please try again.'
    
    @staticmethod
    def update_user(username, password, bio):
        user = User.query.filter_by(username=username).first()
        if user:
            if password and len(password) >= 8:
                user.set_password(password)
                db.session.commit()
            if bio and (0 < len(bio) < 200):
                user.bio = bio
                db.session.commit()
            return True, user
        else:
            return False, None

    def to_dict(self):
        return {
            'id': self.id, 
            'username': self.username,
            'bio': self.bio,
            'avatar_url': self.avatar_url,
            'favorites': [favorite.to_dict() for favorite in self.favorites]
        }

    # Print user object
    def __repr__(self):
        return f"User('{self.username}')"