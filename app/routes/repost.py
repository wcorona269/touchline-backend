from flask import Blueprint, request, jsonify
from ..models.repost_model import Repost
from sqlalchemy import desc

bp = Blueprint('repost', __name__, url_prefix='/reposts')

@bp.route('/create', methods=['POST'])
def create_repost():
    data = request.json
    user_id = data.get('user_id')
    post_id = data.get('post_id')

    if not user_id or not post_id:
        return jsonify({
            'message': 'Invalid request data.'
            }), 400
        
    success, repost = Repost.add_repost(user_id, post_id)
    if success == True:
        return jsonify({
            'message': 'Repost created successfully',
            'repost': repost.to_dict()
            }), 200
    else:
        return jsonify({
                'message': 'Repost creation failed'
            }), 401

@bp.route('/delete', methods=['DELETE'])
def delete_repost():
    data = request.get_json()
    user_id = data.get('user_id')
    post_id = data.get('post_id')

    if not user_id or not post_id:
        return jsonify({
            'message': 'Invalid request data.'
        }), 400

    success, repostId = Repost.delete_repost(user_id=user_id, post_id=post_id)
    if success == True:
        return jsonify({
                'message': 'Repost deleted successfully',
                'repostId': repostId
            }), 200
    else:
        return jsonify({
                'message': 'Repost deletion failed - Invalid request'
            }), 401

@bp.route('/fetch/<userId>', methods=['GET'])
def fetch_user_reposts(userId):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    reposts = Repost.query.filter_by(user_id=userId).order_by(Repost.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    if not reposts.items:
        return jsonify({'message': 'no reposts found'}), 404

    normalized_reposts = { repost.id: repost.to_dict() for repost in reposts.items }

    return jsonify({
        'message': 'All posts retrieved successfully',
        'posts': normalized_reposts,
        'total_pages': reposts.pages,
        'current_page': reposts.page,
        'total_reposts': reposts.total
    }), 200

@bp.route('/index', methods=['GET'])
def get_all_reposts():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    reposts = Repost.query.order_by(Repost.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    if not reposts.items:
        return jsonify({'message': 'no posts found'}), 404

    reposts_data = { repost.id: repost.to_dict() for repost in reposts.items }


    if reposts:
        return jsonify({
                'message': 'Reposts fetched successfully',
            'reposts': reposts_data
            }), 200
    else:
        return jsonify({
                'message': 'Reposts fetch failed'
            }), 401

@bp.route('/fetch/one/<id>', methods=['GET'])
def fetch_repost(id):
    repost = Repost.query.get(id)
    repost_data = repost.to_dict()
    if repost_data:
        return jsonify({
                'message': 'Repost found sucessfully',
                'repost': repost_data
            }), 200
    else:
        return jsonify({
                'message': 'Repost not found'
            }), 404