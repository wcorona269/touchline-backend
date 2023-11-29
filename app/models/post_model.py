from .db import db
from .user_model import User
from datetime import datetime, timezone, timedelta


class Post(db.Model):
  __tablename__ = 'posts'
  
  server_timezone_offset = -5
  local_time = datetime.now(timezone.utc) + timedelta(hours=server_timezone_offset)
  # posts table columns
  id = db.Column(db.Integer, primary_key=True, index=True, nullable=False)
  text = db.Column(db.String(200), nullable=False)
  user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True, nullable=False)
  created_at = db.Column(db.DateTime, default=local_time, nullable=False)
  # relationships
  user = db.relationship('User', back_populates='posts')
  likes = db.relationship('PostLike', back_populates='post')
  comments = db.relationship('Comment', back_populates='post')
  reposts = db.relationship('Repost', back_populates='post')
  
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
      print(f"Error deleting post: {str(e)}")
      return False;

  def to_dict(self):
    user_instance = User.query.get(self.user_id)
    user_data = User.to_dict(user_instance) if user_instance else None
    
    return {
			'id': self.id,
			'user_id': self.user_id,
			'username': user_data['username'],
      'avatar_url': user_data['avatar_url'],
			'text': self.text,
			'likes': [like.to_dict() for like in self.likes],
			'comments': [comment.to_dict() for comment in self.comments],
      'reposts': [repost.user_info() for repost in self.reposts],
			'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
		}
    
def __repr__(self):
	return f'<Post {self.id}>'