from flask import Blueprint, request, jsonify, make_response
from ..models import db, User
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import jwt
from ..config import Config
import datetime

bp = Blueprint('auth', __name__, url_prefix='/auth')
revoked_tokens = set()

@bp.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    success, details = User.register_user(username, password)
    if success:
        user_data = details.to_dict()  
        return jsonify({
                'message': 'User Created Successfully',
                'user': user_data
        }), 201
    else:
        return jsonify({
                'message': details
            }), 400

@bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    status, info = User.login_user(username, password)
    if status:
        token = jwt.encode({
            'username': info['username'], 
            'id': info['id'], 
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=6)}, Config.SECRET_KEY, algorithm='HS256')
        response = make_response(jsonify({
                'message': 'Login successful',
                'user': info
        }))
        response.set_cookie('access_token', token, httponly=True, secure=True)
        # response.headers.add('Set-Cookie','cross-site-cookie=bar; SameSite=Strict; Secure')
        return response, 200
    else:
        print(info)
        return jsonify({
                'message': info
        }), 401

@bp.route('/logout', methods=['POST'])
def logout():
    response = make_response(jsonify({'message': 'Logout successful'}))
    response.set_cookie('access_token', '', expires=0, httponly=True, secure=True)
    return response, 200