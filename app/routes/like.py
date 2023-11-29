from flask import Blueprint, request, jsonify
from ..models.like_model import PostLike, CommentLike

bp = Blueprint('likes', __name__, url_prefix='/likes')

@bp.route('/create', methods=['POST'])
def create_like():
  data = request.json
  user_id = data.get('user_id')
  post_id = data.get('post_id')
  comment_id = data.get('comment_id')
  
  if not user_id:
    return jsonify({
			'message': 'Invalid request data'
		}), 400
    
  if user_id and post_id:
    PostLike.add_like(user_id, post_id)
    return jsonify({
			'message': 'Like created successfully'
		}), 200
  
  if user_id and comment_id:
    CommentLike.add_like(user_id, comment_id)
    return jsonify({
			'message': 'Like created successfully',
		}), 200
  
  return jsonify({
		'message': 'Invalid request data'
	}), 400
  

@bp.route('/delete', methods=['DELETE'])
def delete_like():
	data = request.json
	user_id = data.get('user_id')
	post_id = data.get('post_id')
	comment_id = data.get('comment_id')
  
	if user_id and post_id:
		post_like = PostLike.delete_like(user_id, post_id)
		if post_like == True:
			return jsonify({
				'message': 'Post Like delected successfully'
			}), 200
  
	if user_id and comment_id:
		comment_like = CommentLike.delete_like(user_id, comment_id)
		if comment_like == True:
			return jsonify({
				'message': 'Comment Like delected successfully'
			}), 200
  
	return jsonify({
		'message': 'Invalid request data'
	}), 400