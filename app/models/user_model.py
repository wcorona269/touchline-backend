from flask_login import UserMixin, login_user, login_required
from sqlalchemy import CheckConstraint
from datetime import timedelta
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from .db import db, bcrypt
from flask import jsonify
from datetime import datetime, timezone, timedelta

class User(UserMixin, db.Model):
	__tablename__ = 'users'
 
	server_timezone_offset = -5
	local_time = datetime.now(timezone.utc) + timedelta(hours=server_timezone_offset)
 
	# table columns
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True, nullable=False)
	bio = db.Column(db.String(200), default='', nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=False)
	password_hash = db.Column(db.String(255), nullable=False)
	created_at = db.Column(db.DateTime, default=local_time, nullable=False)
	avatar_url = db.Column(db.String(255), default='', nullable=True)
	bio = db.Column(db.String, default='')
 
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
	)
	
	# getter methods
	def get_id(self):
		return str(self.id)
 
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
	def find_user_by_email(email):
		user = User.query.filter_by(email=email).first();
		if user:
			return user['username']
		else:
			return 'User not found'

	@staticmethod
	def login_user(email, password):
		if not email or not password:
			return False, None

		user = User.query.filter_by(email=email).first()
    
		if not user or not user.check_password(password):
			return False, None
		else:
			user_data = {
				'id': user.id,
				'email': user.email,
				'username': user.username
			}
			return True, user_data

  # Register User
	@staticmethod
	def register_user(email, username, password):
		if not username or not email or not password:
			return False
		
		if User.query.filter_by(username=username).first():
			return False
   
		if User.query.filter_by(email=email).first():
			return False

		user = User(username=username, email=email)
		user.set_password(password)
		db.session.add(user)
		db.session.commit()

		return True

	@staticmethod
	def update_user(username, password):
		user = User.query.filter_by(username=username).first()
		if user:
			if password:
				user.set_password(password)
				db.session.commit()
				return True;
			# if bio:
			# 	user.set_bio(bio)
			# 	db.session.commit()
			# 	return True
		else:
			return False;

	def to_dict(self):
		return {
			'id': self.id, 
			'username': self.username,
			'email': self.email,
			'bio': self.bio,
			'avatar_url': self.avatar_url,
			'favorites': [favorite.to_dict() for favorite in self.favorites]
		}

	# Print user object
	def __repr__(self):
		return f"User('{self.username}', '{self.email}')"
