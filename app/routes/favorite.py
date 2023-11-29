from flask import Blueprint, request, jsonify
from ..models.favorite_model import Favorite, FavoriteType

bp = Blueprint('favorite', __name__, url_prefix='/favorite')

def map_target_type(target_type):
  type_mapping = {
      'PLAYER': FavoriteType.PLAYER,
      'CLUB': FavoriteType.CLUB,
      'LEAGUE': FavoriteType.LEAGUE,
  }
  
  return type_mapping.get(target_type, None)


@bp.route('/fetch/<int:userId>', methods=['GET'])
def fetch_user_favorites(userId):
    success, favorites = Favorite.get_user_favorites(userId)
    if success:
        return jsonify({
            'message': 'favorites fetched successfully',
            'favorites': favorites
        }), 200
    else:
        return jsonify({
            'message': 'Favorites not found'
        }), 404

@bp.route('/create', methods=['POST'])
def add_favorite():
    data = request.json
    user_id, name, target_id, target_type_str = data.get('user_id'), data.get('name'), data.get('target_id'), data.get('target_type')
    target_type = map_target_type(target_type_str)
    success, favorite = Favorite.add_favorite(user_id, name, target_type, target_id)
    if success:
        return jsonify({
                'message': 'Favorite created successfully',
                'favorite': favorite.to_dict()
            }), 200
    else:
        return jsonify({
                'message': 'Invalid request data'
		}), 401
            
@bp.route('/delete/<int:favId>', methods=['DELETE'])
def delete_fav(favId):
    fav = Favorite.query.get(favId)
    if fav:
        fav.delete_favorite()
        return jsonify({
                'message': 'Favorite deleted successfully',
                'id': favId
            }), 200
    else:
        return jsonify({
                'message': 'Favorite not found - invalid request data'
            }), 401