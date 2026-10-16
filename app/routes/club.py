import logging
from flask import jsonify
from .news_feeds import club_news
from .slim import slim_fixtures
from .parallel import run_parallel
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
    club_info, squad_data, fixtures = run_parallel(
        lambda: cached_api_get(f"/teams?id={clubId}", DAY),
        lambda: cached_api_get(f"/players/squads?team={clubId}", 12 * HOUR),
        lambda: cached_api_get(f"/fixtures?team={clubId}&season={season}", season_ttl(season, 10 * MINUTE)),
    )

    # Stats are per competition, so they depend on which competitions the fixtures cover.
    competition_ids = list(dict.fromkeys(fixture['league']['id'] for fixture in fixtures))
    *competition_stats, cleaned_news = run_parallel(
        *[lambda competition_id=competition_id: cached_api_get(
            f"/teams/statistics?team={clubId}&season={season}&league={competition_id}", season_ttl(season, HOUR)
        ) for competition_id in competition_ids],
        lambda: club_news(club_info[0]['team']['name']),
    )
    # Competitions with no matches played yet come back as an empty list rather than a stats object.
    club_stats = [stats for stats in competition_stats if stats and isinstance(stats, dict)]

    combined_data = {
            'club': club_info,
            'squad': squad_data,
            'fixtures': slim_fixtures(fixtures),
            'stats': club_stats,
            'news': cleaned_news
    }

    return combined_data
