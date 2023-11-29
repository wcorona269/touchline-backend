from .db import db
from .user_model import User

class PostLike(db.Model):
	__tablename__ = 'post_likes'

	id = db.Column(db.Integer, primary_key=True, index=True, nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True, nullable=False)
	post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), index=True, nullable=False)
	user = db.relationship('User', back_populates='likes')
	post = db.relationship('Post', back_populates='likes')
	
	def add_like(user_id, post_id):
		new_like = PostLike(user_id=user_id, post_id=post_id)
		db.session.add(new_like)
		db.session.commit()

	def delete_like(user_id, post_id):
		like_to_delete = PostLike.query.filter_by(user_id=user_id, post_id=post_id).first()

		if like_to_delete:
			db.session.delete(like_to_delete)
			db.session.commit()
			return True
		else:
			return False
 
	def to_dict(self):
		user_instance = User.query.get(self.user_id)
		user_data = User.to_dict(user_instance) if user_instance else None
		return {
			'id': self.id,
			'user_id': self.user_id,
			'post_id': self.post_id
		}


class CommentLike(db.Model):
	__tablename__ = 'comment_likes'

	id = db.Column(db.Integer, primary_key=True, index=True, nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True, nullable=False)
	comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'), index=True, nullable=False)
	comment = db.relationship('Comment', back_populates='comment_likes')

	def add_like(user_id, comment_id):
		new_like = CommentLike(user_id=user_id, comment_id=comment_id)
		db.session.add(new_like)
		db.session.commit()

	def delete_like(user_id, comment_id):
		like_to_delete = CommentLike.query.filter_by(user_id=user_id, comment_id=comment_id).first()
  
		if like_to_delete:
			db.session.delete(like_to_delete)
			db.session.commit()
			return True
		else:
			return False
 
	def to_dict(self):
		user_instance = User.query.get(self.user_id)
		user_data = User.to_dict(user_instance) if user_instance else None;
  
		return {
			'id': self.id,
			'user_id': self.user_id ,
			'comment_id': self.comment_id
		}