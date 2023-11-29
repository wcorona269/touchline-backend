from sqlalchemy import desc
from flask import Blueprint, request, jsonify
from ..models import  db, Comment

bp = Blueprint('comments', __name__, url_prefix='/comments')

@bp.route('/create', methods=['POST'])
def create_comment():
  data = request.json
  user_id = data.get('user_id')
  post_id = data.get('post_id')
  text = data.get('text')
  parent_id = data.get('parent_id')
  
  if not text:
    return jsonify({
			'message': 'Missing required text field'
		}), 400
    
  if user_id and post_id and text and not parent_id:
    new_comment = Comment(user_id=user_id, post_id=post_id, text=text, parent_id=None)
    db.session.add(new_comment)
    db.session.commit()
    return jsonify({
        'message': 'Comment created successfully',
        'comment': new_comment.to_dict()
    }), 200
    
  if user_id and post_id and text and parent_id:
    new_comment = Comment(user_id=user_id, post_id=post_id, text=text, parent_id=parent_id)
    db.session.add(new_comment)
    db.session.commit()
    return jsonify({
        'message': 'Comment created successfully'
    }), 200
  
  return ({
		'message': 'Invalid request data'
	}), 400
  

@bp.route('/delete', methods=['DELETE'])
def delete_comment():
  data = request.json
  id = data.get('id')
  
  if id:
    comment = Comment.delete_comment(id)
    if comment == True:
      return jsonify({
				'message': 'Comment deleted successfully'
			}), 200
    else:
      return jsonify({
				'message': 'invalid request data'
			}), 400