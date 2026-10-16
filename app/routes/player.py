from flask import request
import logging
from flask import Blueprint, jsonify
from ..extensions import cache
from .api_football import cached_api_get, is_success, ApiFootballError, season_ttl, HOUR
from .seasons import current_season

bp = Blueprint('players', __name__, url_prefix='/players')

@bp.route('/<playerId>', methods=['GET'])
@cache.cached(timeout=3600, response_filter=is_success)
def competitionInfo(playerId):
  try:
    return _player_info(playerId)
  except ApiFootballError as e:
    logging.warning("api-sports error in %s: %s", request.path, e)
    return jsonify({'error': 'The football data provider is temporarily unavailable. Try again in a minute.'}), 503


def _player_info(playerId):

  # A player with no appearances yet this season comes back empty, so fall back to last season.
  season = current_season()
  for attempt in (season, season - 1):
    player_data = cached_api_get(f"/players?id={playerId}&season={attempt}", season_ttl(attempt, 6 * HOUR))
    if player_data:
      break
  return player_data