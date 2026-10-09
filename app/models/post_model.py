import logging
from .db import db
from .user_model import User
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)

class Post(db.Model):
    __tablename__ = 'posts'

    # posts table columns
    id = db.Column(db.Integer, primary_key=True, index=True, nullable=False)
    text = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True, nullable=False)
    created_at = db.Column(db.DateTime, default=func.now(), nullable=False)
    # relationships
    user = db.relationship('User', back_populates='posts', lazy='joined')
    likes = db.relationship('PostLike', back_populates='post', cascade='all, delete-orphan', lazy='selectin')
    comments = db.relationship('Comment', back_populates='post', cascade='all, delete-orphan', lazy='selectin')
    reposts = db.relationship('Repost', back_populates='post', cascade='all, delete-orphan', lazy='selectin')
    
    @staticmethod
    def create_post(user_id, text):
        try:
            post = Post(user_id=user_id, text=text)
            db.session.add(post)
            db.session.commit()
            return True, post.to_dict()
        except IntegrityError as e:
            db.session.rollback()
            logger.exception('Error creating post')
            return False, e

    @staticmethod
    def delete_post(id):
        try:
            post_to_delete = Post.query.get(id)
            if post_to_delete:
                db.session.delete(post_to_delete)
                db.session.commit()
                return True
            else:
                return False
        except Exception as e:
            db.session.rollback()
            logger.exception('Error deleting post')
            return False;
        
    def to_dict(self):
        user_data = self.user.to_dict() if self.user else None

        return {
                'id': self.id,
                'user_id': self.user_id,
                'username': user_data['username'],
                'avatar_url': user_data['avatar_url'],
                'text': self.text,
                'likes': [like.to_dict() for like in self.likes],
                'comments': [comment.to_dict() for comment in self.comments],
                'reposts': [repost.user_info() for repost in self.reposts],
                'created_at': self.created_at.strftime('%Y-%m-%dT%H:%M:%SZ')
            }

    def __repr__(self):
        return f'<Post {self.id}>'