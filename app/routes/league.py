from flask import request
import logging
from flask import Blueprint, jsonify
from .news_feeds import league_news
from .league_ids import get_league_ids
from ..extensions import cache
from .api_football import cached_api_get, is_success, ApiFootballError, season_ttl, MINUTE, HOUR, DAY


bp = Blueprint('league', __name__, url_prefix='/leagues')

@bp.route('/index', methods=['GET'])
@cache.cached(timeout=3600)
def fetchAllComps():
    ids = get_league_ids()
    
    
    # Make the first API call to get standings
    league_data = cached_api_get("/leagues?current=True", DAY)
    top_league_ids = set([2, 3, 39, 78, 135, 61, 140, 253 ])
    top_leagues = {}
    filtered_leagues = {}
    for ele in league_data:
        id = int(ele['league']['id'])
        if id in top_league_ids:
            top_leagues[id] = ele
        
        if id in ids:
            nation = ele['country']['name']
            if nation not in filtered_leagues:
                filtered_leagues[nation] = {}
            filtered_leagues[nation][int(id)] = ele

    return jsonify({
        'top_leagues': top_leagues,
        'all_leagues': filtered_leagues
    }), 200


@bp.route('/<leagueId>/<season>', methods=['GET'])
@cache.cached(timeout=300, response_filter=is_success)
def competitionInfo(leagueId, season):
    try:
        return _competition_info(leagueId, season)
    except ApiFootballError as e:
        logging.warning("api-sports error in %s: %s", request.path, e)
        return jsonify({'error': 'The football data provider is temporarily unavailable. Try again in a minute.'}), 503


def _competition_info(leagueId, season):

    # Make the first API call to get standings
    standings_data = cached_api_get(f"/standings?league={leagueId}&season={season}", season_ttl(season, 10 * MINUTE))

    # Get top scorer data
    top_scorer_data = cached_api_get(f"/players/topscorers?season={season}&league={leagueId}", season_ttl(season, HOUR))

    # Top assists data
    top_assists_data = cached_api_get(f"/players/topassists?season={season}&league={leagueId}", season_ttl(season, HOUR))

    # Fixture data
    fixture_data = cached_api_get(f"/fixtures?season={season}&league={leagueId}", season_ttl(season, 10 * MINUTE))

    # fetch competition news
    cleaned_news = league_news(leagueId, standings_data[0]['league']['name'])

    # combine data and return to frontend
    combined_data = {
            "standings": standings_data,
            "top scorers": top_scorer_data,
            "top assists": top_assists_data,
            "fixtures": fixture_data,
            "news": cleaned_news,
    }

    return combined_data