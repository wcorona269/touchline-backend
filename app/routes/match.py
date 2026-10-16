import logging
from flask import Blueprint, jsonify, request
from .api_football import cached_api_get, ApiFootballError, MINUTE, WEEK

bp = Blueprint('match', __name__, url_prefix='/match')

FINISHED = {'FT', 'AET', 'PEN', 'CANC', 'ABD', 'AWD', 'WO'}
# Postponed matches get rescheduled, so they're treated like upcoming ones.
NOT_STARTED = {'NS', 'TBD', 'PST'}


def match_ttl(response):
    """Finished matches never change; live ones change by the minute."""
    status = response[0]['fixture']['status']['short'] if response else None
    if status in FINISHED:
        return WEEK
    if status in NOT_STARTED:
        return 10 * MINUTE
    return MINUTE


@bp.route('/<matchId>', methods=['GET'])
def get_match_info(matchId):
  try:
    return jsonify(cached_api_get(f"/fixtures?id={matchId}", match_ttl))
  except ApiFootballError as e:
    logging.warning("api-sports error in %s: %s", request.path, e)
    return jsonify({'error': 'The football data provider is temporarily unavailable. Try again in a minute.'}), 503
