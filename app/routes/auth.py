from flask import Blueprint, request, jsonify, make_response
from ..models import db, User
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import jwt
from ..config import Config
import datetime

bp = Blueprint('auth', __name__, url_prefix='/auth')

# Create a set of revoked session tokens
revoked_tokens = set()

@bp.route('/register', methods=['POST'])
def register():
  data = request.json
  username = data.get('username')
  password = data.get('password')
  
  new_user = User.register_user(username, password)
  
  if new_user == True:
    return jsonify({'message': 'User Created Successfully'}), 200
  else:
    return jsonify({'message': 'Invalid credentials'}), 400

@bp.route('/login', methods=['POST'])
def login():
  data = request.json
  username = data.get('username')
  password = data.get('password')
  
  status, user = User.login_user(username, password)
  if status == True:
    token = jwt.encode({'username': user['username'], 'id': user['id'], 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=6)}, Config.SECRET_KEY, algorithm='HS256')
    response = make_response(jsonify({
      'message': 'Login successful',
      'user': user
    }))
    response.set_cookie('access_token', token, httponly=True, secure=True)
    # response.headers.add('Set-Cookie','cross-site-cookie=bar; SameSite=Strict; Secure')
    return response, 200
  else:
    return jsonify({
      'message': 'Login attempt failed'
    }), 401

@bp.route('/logout', methods=['POST'])
def logout():
  response = make_response(jsonify({'message': 'Logout successful'}))
  response.set_cookie('access_token', '', expires=0, httponly=True, secure=True)
  return response, 200

@bp.route('/update/', methods=['POST'])
def update_user():
    data = request.json;
    username = data.get('username')
    password = data.get('password')
    bio = data.get('bio')
    result, user = User.update_user(username, password, bio)
    if result:
      user_info = user.to_dict()
      return jsonify({
        'message': 'user updated successfully',
        'user': user_info
      }), 200
    else:
      return jsonify({
        'message': 'User update failed'
      }), 500