import logging
from datetime import date as Date, timedelta
from flask import Blueprint, jsonify, request
from .league_ids import get_league_ids
from .api_football import cached_api_get, ApiFootballError, MINUTE, WEEK

bp = Blueprint('matches', __name__, url_prefix='/matches')

UNAVAILABLE = {'error': 'The football data provider is temporarily unavailable. Try again in a minute.'}


def date_ttl(date):
    """Days that are fully over never change. Yesterday and today can still have games in
    progress somewhere (dates are UTC), and future fixtures only shift occasionally."""
    try:
        day = Date.fromisoformat(date)
    except ValueError:
        return 2 * MINUTE
    today = Date.today()
    if day < today - timedelta(days=1):
        return WEEK
    if day <= today:
        return 2 * MINUTE
    return 30 * MINUTE


@bp.route('/<date>', methods=['GET'])
def matches(date):
    try:
        matches_of_the_day = cached_api_get(f"/fixtures?date={date}", date_ttl(date))
    except ApiFootballError as e:
        logging.warning("api-sports error in %s: %s", request.path, e)
        return jsonify(UNAVAILABLE), 503
    
    ids = get_league_ids()
    filtered_matches = [match for match in matches_of_the_day if match['league']['id'] in ids]
    
    if matches_of_the_day:
        return jsonify({
            'message': 'Matches fetched successfully',
            'matches': filtered_matches
        }), 200
    else:
        return jsonify({
            'message': 'Matches not found'
        }), 401


@bp.route('/live', methods=['GET'])
def liveMatches():
    try:
        live_matches = cached_api_get("/fixtures?live=all", MINUTE)
    except ApiFootballError as e:
        logging.warning("api-sports error in %s: %s", request.path, e)
        return jsonify(UNAVAILABLE), 503
    ids = get_league_ids()
    filtered_matches = [match for match in live_matches if match['league']['id'] in ids]
    
    if live_matches:
        return jsonify({
            'message': 'Matches fetched successfully',
            'matches': filtered_matches
            }), 200
    else:
        return jsonify({
            'message': 'Matches not found'
        }), 401