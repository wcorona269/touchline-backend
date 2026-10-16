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
    conn = http.client.HTTPSConnection("v3.football.api-sports.io")
    headers = {
        'x-rapidapi-host': "v3.football.api-sports.io",
        'x-rapidapi-key': api_key
    }

    standings = api_get(f"/standings?league={leagueId}&season={season}", conn)
    if standings:  
        return jsonify({
            'message': 'Standings fetched successfully',
            'standings': standings
        }), 200
    else:
        return jsonify({
            'error': 'Error fetching league standings'
        }), 401