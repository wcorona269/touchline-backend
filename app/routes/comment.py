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

    success, response_data = Comment.create_comment(user_id, post_id, text, parent_id)
    if success:
        return jsonify({
            'message': 'Comment created successfully',
            'comment': response_data
        }), 200
    else:
        return jsonify({
            'error': 'invalid request data'
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