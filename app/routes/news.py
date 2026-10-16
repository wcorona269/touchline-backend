import logging
from flask import Blueprint, request, jsonify
from .news_feeds import general_news, personalized_news

logger = logging.getLogger(__name__)
bp = Blueprint('news', __name__, url_prefix='/news')

# No route-level caching: Flask-Caching keys on the path, not the POST body, so it served every
# user the first requester's personalized feed. The feeds themselves are cached in news_feeds.

@bp.route('/all', methods=['POST'])
def fetchNews():
    try:
        fav_names = request.json.get('favNames', []) if request.json else []
        return jsonify({
            'message': 'News fetched successfully',
            'news': personalized_news(fav_names),
        }), 201
    except Exception as e:
        logger.exception('Failed to fetch news')
        return jsonify({'error': str(e)}), 500

@bp.route('/top', methods=['POST'])
def fetchTopNews():
    try:
        return jsonify({
            'message': 'News fetched successfully',
            'news': general_news()[:10],
        }), 201
    except Exception as e:
        logger.exception('Failed to fetch top news')
        return jsonify({'error': str(e)}), 500
