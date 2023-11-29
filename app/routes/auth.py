from flask import Blueprint, request, jsonify, make_response
from ..models import db, User
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import jwt
from ..config import Config
import datetime
from datetime import timedelta


bp = Blueprint('auth', __name__, url_prefix='/auth')

# Create a set of revoked session tokens
revoked_tokens = set()

@bp.route('/register', methods=['POST'])
def register():
  data = request.json
  username = data.get('username')
  email = data.get('email')
  password = data.get('password')
  
  new_user = User.register_user(email, username, password)
  
  if new_user == True:
    return jsonify({'message': 'User Created Successfully'}), 200
  else:
    return jsonify({'message': 'Invalid credentials'}), 400

@bp.route('/login', methods=['POST'])
def login():
  data = request.json
  email = data.get('email')
  password = data.get('password')
  
  status, message = User.login_user(email, password)
  if status == True:
    token = jwt.encode({'email': email, 'username': message['username'], 'id': message['id'], 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=6)}, Config.SECRET_KEY, algorithm='HS256')
    response = make_response(jsonify({'message': 'Login successful'}))
    response.set_cookie('access_token', token, httponly=True, secure=True)
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
    bio = data.get('password')
    result = User.update_user(username, password)
    if result:
      return jsonify({
        'message': 'user updated successfully'
      }), 201
    else:
      return jsonify({
        'message': 'User update failed'
      }), 500