from datetime import datetime, timezone, timedelta
from .user_model import User
from .db import db

class Comment(db.Model):
	__tablename__ = 'comments'
 
	server_timezone_offset = -5
	local_time = datetime.now(timezone.utc) + timedelta(hours=server_timezone_offset)
	id = db.Column(db.Integer, primary_key=True, index=True, nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True, nullable=False)
	post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), index=True, nullable=False)  # Define foreign key to 'posts.id'

	text = db.Column(db.String(200), nullable=False)
	created_at = db.Column(db.DateTime, default=local_time)
	parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'), default=None)
 
	user = db.relationship('User', back_populates='comments')
	post = db.relationship('Post', back_populates='comments', foreign_keys=[post_id])
	parent_comment = db.relationship('Comment', remote_side=[id], back_populates='replies')
	replies = db.relationship('Comment', back_populates='parent_comment')
	comment_likes = db.relationship('CommentLike', back_populates='comment')

	def to_dict(self):
		user_instance = User.query.get(self.user_id)
		user = user_instance.to_dict()

		return {
			'id': self.id,
			'user_id': self.user_id,
			'post_id': self.post_id,
			'text': self.text,
			'likes': [like.to_dict() for like in self.comment_likes],
			'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'username': user['username'],
			'avatar_url': user['avatar_url'],
			'parent_id': self.parent_id,
			# Add other fields as needed
		}
    
	def delete_comment(id):
		comment_to_delete = Comment.query.filter_by(id=id).first()

		if (comment_to_delete):
			db.session.delete(comment_to_delete)
			db.session.commit()
			return True
		else:
			return False
  
	def __repr__(self):
			return f'<Comment {self.id}>'