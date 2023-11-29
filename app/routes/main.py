
from flask import Blueprint, redirect, jsonify
from ..models import User, Favorite
import requests

bp = Blueprint('home', __name__)

@bp.route('/')
def home():
    users = User.query.order_by(User.id).all()
    favorites = Favorite.query.order_by(Favorite.user_id).all()    
    return f'{users}, {favorites}'