from flask import request
import logging
from flask import Blueprint, jsonify
from ..extensions import cache
from .api_football import cached_api_get, is_success, ApiFootballError, season_ttl, MINUTE
from .seasons import current_season

bp = Blueprint('standings', __name__, url_prefix='/standings')

@bp.route('/<leagueId>', methods=['GET'])
@bp.route('/<leagueId>/<int:season>', methods=['GET'])
@cache.cached(timeout=300, response_filter=is_success)
def fetch_standings(leagueId, season=None):
    try:
        return _fetch_standings(leagueId, season or current_season())
    except ApiFootballError as e:
        logging.warning("api-sports error in %s: %s", request.path, e)
        return jsonify({'error': 'The football data provider is temporarily unavailable. Try again in a minute.'}), 503


def _fetch_standings(leagueId, season):

    standings = cached_api_get(f"/standings?league={leagueId}&season={season}", season_ttl(season, 10 * MINUTE))
    if standings:  
        return jsonify({
            'message': 'Standings fetched successfully',
            'standings': standings
        }), 200
    else:
        return jsonify({
            'error': 'Error fetching league standings'
        }), 401