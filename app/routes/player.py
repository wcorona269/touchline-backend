from flask import request
import logging
import json
import os
from flask import Blueprint, jsonify
import http.client
from dotenv import load_dotenv
from ..extensions import cache
from .api_football import api_get, is_success, ApiFootballError
from .seasons import current_season
load_dotenv(".flaskenv")
api_key = os.getenv("API_KEY")

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
  conn = http.client.HTTPSConnection("v3.football.api-sports.io")
  headers = {
      'x-rapidapi-host': "v3.football.api-sports.io",
      'x-rapidapi-key': api_key
  }

  # A player with no appearances yet this season comes back empty, so fall back to last season.
  season = current_season()
  for attempt in (season, season - 1):
    player_data = api_get(f"/players?id={playerId}&season={attempt}", conn)
    if player_data:
      break
  return player_data