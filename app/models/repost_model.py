from .db import db
from .user_model import User
from .post_model import Post
from datetime import datetime, timezone, timedelta

class Repost(db.Model):
  __tablename__ = 'reposts'
  
  server_timezone_offset = -5
  local_time = datetime.now(timezone.utc) + timedelta(hours=server_timezone_offset)
  # repost table columns
  id = db.Column(db.Integer, primary_key=True, nullable=False)
  user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
  post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
  created_at = db.Column(db.DateTime, default=local_time, nullable=False)
  # relationships
  user = db.relationship('User', backref='reposts', lazy='joined')
  post = db.relationship('Post', back_populates='reposts', lazy='joined')
  
  @staticmethod
  def add_repost(user_id, post_id):
    try:
      new_repost = Repost(user_id=user_id, post_id=post_id)
      db.session.add(new_repost)
      db.session.commit()
      return True, new_repost
    except Exception as e:
      db.session.rollback()  # Rollback the session in case of an error
      print(f"Error adding repost: {str(e)}")
      return False, None
    
  @staticmethod
  def delete_repost(user_id, post_id):
    try:
      repost_to_delete = Repost.query.filter_by(user_id=user_id, post_id=post_id).first()
      if repost_to_delete:
        db.session.delete(repost_to_delete)
        db.session.commit()
        return True, repost_to_delete.id
      else:
        return False
    except Exception as e:
      db.session.rollback()  # Rollback the session in case of an error
      print(f"Error deleting repost: {str(e)}")
      return False, None
    
  
  def user_info(self):
    user_data = self.user.to_dict() if self.user else None;
    return user_data
      
  def to_dict(self):
    user_data = self.user.to_dict() if self.user else None
    post_data = self.post.to_dict() if self.post else None
    return {
				'id': self.id,
				'user': user_data,
				'post': post_data,
        'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
		}