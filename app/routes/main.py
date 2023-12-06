
from flask import Blueprint, redirect, jsonify
from ..models import User, Favorite
import requests

bp = Blueprint('home', __name__, url_prefix='/home')

@bp.route('/')
def home():
    user = User.query.order_by(User.id).first()
    return jsonify({
        'message': 'home',
        'user': user.to_dict()
    })