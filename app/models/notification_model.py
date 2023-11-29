from .db import db
from .user_model import User
from enum import Enum
from datetime import datetime, timezone, timedelta

class NotificationType(Enum):
    POST_LIKE = 'post_like'
    POST_COMMENT = 'post_comment'
    COMMENT_LIKE = 'comment_like'
    REPOST = 'repost'

class Notification(db.Model):
	__tablename__ = 'notifications'
 
	server_timezone_offset = -5
	local_time = datetime.now(timezone.utc) + timedelta(hours=server_timezone_offset)
	id = db.Column(db.Integer, primary_key=True)
	sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
	recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
	target_id = db.Column(db.Integer, nullable=False)  # ID of the target entity (e.g., post_id, comment_id)
	target_type = db.Column(db.Enum(NotificationType), nullable=False)  # Type of the target entity
	created_at = db.Column(db.DateTime, default=local_time, nullable=False)
	read = db.Column(db.Boolean, nullable=False, default=False)
	sender = db.relationship('User', back_populates='notifications_sent', foreign_keys=[sender_id])
	recipient = db.relationship('User', back_populates='notifications_received', foreign_keys=[recipient_id])

	def add_notification(recipient_id, sender_id, target_type, target_id, created_at, read):
		if sender_id == recipient_id:
			return False
		new_notif = Notification(recipient_id=recipient_id, sender_id=sender_id, target_type=target_type, target_id=target_id, created_at=created_at, read=read)
		if new_notif:
			db.session.add(new_notif)
			db.session.commit()  
			return True
		else:
			return False
 
	def delete_notification(id):
		notif_to_delete = Notification.query.get(id)
		if notif_to_delete:
			db.session.delete(notif_to_delete)
			db.session.commit()
			return True
		else:
			return False
 
	def set_as_read(id):
		notif_to_read = Notification.query.get(id)
		if notif_to_read:
			notif_to_read.read = True
			db.session.commit()  # Commit the changes to the database
			return True, notif_to_read
		else:
			return False, None
 
	def read_all(user_id):
		user = User.query.get(user_id)
		if user:
			for notif in user.notifications_received:
				notif.read = True
				db.session.commit()
			return True, user.notifications_received
		else:
			return False
 
	def to_dict(self):
		return {
			'id': self.id,
			'sender_id': self.sender_id,
			'recipient_id': self.recipient_id,
			'target_id': self.target_id,
			'target_type': self.target_type.value,
			'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'read': self.read,
   		'sender': self.sender.to_dict()
		}
     
	def __repr__(self):
		return f'<Notification {self.id}>'