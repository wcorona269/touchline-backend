from flask import request
import logging
from flask import Blueprint, jsonify
from .news_feeds import league_news
from .slim import slim_fixtures, slim_league_entry
from .parallel import run_parallel
from ..extensions import cache
from .api_football import cached_api_get, is_success, ApiFootballError, season_ttl, MINUTE, HOUR, DAY


bp = Blueprint('league', __name__, url_prefix='/leagues')

@bp.route('/index', methods=['GET'])
@cache.cached(timeout=3600)
def fetchAllComps():
    # The Explore page lists every other league from a static table in the frontend; only these
    # featured leagues come from the API. Sending them slimmed (no season history) keeps the
    # response ~1KB instead of ~1MB.
    league_data = cached_api_get("/leagues?current=True", DAY)
    top_league_ids = {2, 3, 39, 78, 135, 61, 140, 253}
    top_leagues = {
        int(entry['league']['id']): slim_league_entry(entry)
        for entry in league_data if int(entry['league']['id']) in top_league_ids
    }
    return jsonify({'top_leagues': top_leagues}), 200


@bp.route('/<leagueId>/<season>', methods=['GET'])
@cache.cached(timeout=300, response_filter=is_success)
def competitionInfo(leagueId, season):
    try:
        return _competition_info(leagueId, season)
    except ApiFootballError as e:
        logging.warning("api-sports error in %s: %s", request.path, e)
        return jsonify({'error': 'The football data provider is temporarily unavailable. Try again in a minute.'}), 503


def _competition_info(leagueId, season):
    standings_data, top_scorer_data, top_assists_data, fixture_data = run_parallel(
        lambda: cached_api_get(f"/standings?league={leagueId}&season={season}", season_ttl(season, 10 * MINUTE)),
        lambda: cached_api_get(f"/players/topscorers?season={season}&league={leagueId}", season_ttl(season, HOUR)),
        lambda: cached_api_get(f"/players/topassists?season={season}&league={leagueId}", season_ttl(season, HOUR)),
        lambda: cached_api_get(f"/fixtures?season={season}&league={leagueId}", season_ttl(season, 10 * MINUTE)),
    )

    # News searches by the league's name, which comes from the standings.
    cleaned_news = league_news(leagueId, standings_data[0]['league']['name'])

    # combine data and return to frontend
    combined_data = {
            "standings": standings_data,
            "top scorers": top_scorer_data,
            "top assists": top_assists_data,
            "fixtures": slim_fixtures(fixture_data),
            "news": cleaned_news,
    }

    return combined_data