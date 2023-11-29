from sqlalchemy import desc
from flask import Blueprint, request, jsonify
from ..models import db, Post

bp = Blueprint('posts', __name__, url_prefix='/posts')

@bp.route('/create', methods=['POST'])
def create_post():
    data = request.json
    user_id = data.get('user_id')
    text = data.get('text')

    if not text:
        return jsonify({'message': 'Missing required text field'}), 400

    post = Post(user_id=user_id, text=text)
    db.session.add(post)
    db.session.commit()

    return jsonify({
        'message': 'Post created successfully',
        'post': post.to_dict()
    }), 201

@bp.route('/delete/<postId>', methods=['DELETE'])
def delete_post(postId):
    message = Post.delete_post(postId)
    if message == True:
        return jsonify({
            'message': 'Post deleted successfully'
        }), 200
    else:
        return jsonify({
            'message': 'Invalid request data'
        }), 401

@bp.route('/fetch/one/<postId>', methods=['GET'])
def fetch_post(postId):
    post = Post.query.filter_by(id=postId).first();
    if post:
        return jsonify({
            'message': 'Post fetched successfully',
            'post': post.to_dict()
        }), 200
    else:
        return jsonify({
            'message': 'Post not found'
            }), 404

@bp.route('/fetch/<userId>')
def fetch_user_posts(userId):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    posts = Post.query.filter_by(user_id=userId).order_by(Post.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    if not posts.items:
        return jsonify({'message': 'no posts found'}), 404

    normalized_posts = { post.id: post.to_dict() for post in posts.items }

    return jsonify({
        'message': 'All posts retrieved successfully',
        'posts': normalized_posts,
        'total_pages': posts.pages,
        'current_page': posts.page,
        'total_posts': posts.total
    }), 200

@bp.route('/index')
def fetch_all_posts():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    posts = Post.query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    if not posts.items:
        return jsonify({'message': 'no posts found'}), 404

    normalized_posts = { post.id: post.to_dict() for post in posts.items }

    return jsonify({
        'message': 'All posts retrieved successfully',
        'posts': normalized_posts,
        'total_pages': posts.pages,
        'current_page': posts.page,
        'total_posts': posts.total
    }), 200