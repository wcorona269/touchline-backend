import logging
from flask import jsonify
from .news_feeds import club_news
from flask import Blueprint
from ..extensions import cache
from .api_football import cached_api_get, is_success, ApiFootballError, season_ttl, MINUTE, HOUR, DAY

bp = Blueprint('clubs', __name__, url_prefix='/clubs')


@bp.route('/info/<clubId>/<season>', methods=['GET'])
@cache.cached(timeout=300, response_filter=is_success)
def club_info(clubId, season):
    try:
        return _club_info(clubId, season)
    except ApiFootballError as e:
        logging.warning("api-sports error fetching club %s: %s", clubId, e)
        return jsonify({'error': 'The football data provider is temporarily unavailable. Try again in a minute.'}), 503


def _club_info(clubId, season):


    # Request club info
    club_info = cached_api_get(f"/teams?id={clubId}", DAY)

    # Request squad details
    squad_data = cached_api_get(f"/players/squads?team={clubId}", 12 * HOUR)

    # Request club fixtures (previous and upcoming)
    fixtures = cached_api_get(f"/fixtures?team={clubId}&season={season}", season_ttl(season, 10 * MINUTE))

    # Get all competitions for season
    competitions = {} 
    for fixture in fixtures:
        if fixture['league']['name'] not in competitions:
            competitions[fixture['league']['name']] = fixture['league']['id']

    # request stats for each competition from that season
    # compile competitions into club_stats
    club_stats = []
    competition_ids = list(competitions.values())

    for competition_id in competition_ids:
        competition_stats = cached_api_get(f"/teams/statistics?team={clubId}&season={season}&league={competition_id}", season_ttl(season, HOUR))
        # Competitions with no matches played yet come back as an empty list rather than a stats object.
        if competition_stats and isinstance(competition_stats, dict):
            club_stats.append(competition_stats)

    # get club news
    cleaned_news = club_news(club_info[0]['team']['name'])

    combined_data = {
            'club': club_info,
            'squad': squad_data,
            'fixtures': fixtures,
            'stats': club_stats,
            'news': cleaned_news
    }

    return combined_data;
