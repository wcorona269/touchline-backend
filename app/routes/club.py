import logging
from flask import request, jsonify
from GoogleNews import GoogleNews
import json
import os
from flask import Blueprint
import http.client
from dotenv import load_dotenv
from ..extensions import cache
from .api_football import api_get, is_success, ApiFootballError
load_dotenv(".flaskenv")
api_key = os.getenv("API_KEY")

bp = Blueprint('clubs', __name__, url_prefix='/clubs')

headers = {
        'x-rapidapi-host': "v3.football.api-sports.io",
        'x-rapidapi-key': api_key
}

@bp.route('/info/<clubId>/<season>', methods=['GET'])
@cache.cached(timeout=300, response_filter=is_success)
def club_info(clubId, season):
    try:
        return _club_info(clubId, season)
    except ApiFootballError as e:
        logging.warning("api-sports error fetching club %s: %s", clubId, e)
        return jsonify({'error': 'The football data provider is temporarily unavailable. Try again in a minute.'}), 503


def _club_info(clubId, season):
    conn = http.client.HTTPSConnection("v3.football.api-sports.io")


    # Request club info
    club_info = api_get(f"/teams?id={clubId}", conn)

    # Request squad details
    squad_data = api_get(f"/players/squads?team={clubId}", conn)

    # Request club fixtures (previous and upcoming)
    fixtures = api_get(f"/fixtures?team={clubId}&season={season}", conn)

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
        competition_stats = api_get(f"/teams/statistics?team={clubId}&season={season}&league={competition_id}", conn)
        # Competitions with no matches played yet come back as an empty list rather than a stats object.
        if competition_stats and isinstance(competition_stats, dict):
            club_stats.append(competition_stats)

    # get club news
    club_name = club_info[0]['team']['name']
    gNews = GoogleNews(period='20d')
    gNews.get_news(club_name)
    competition_news = gNews.results()
    cleaned_news = []
    for article in competition_news:
        # Create a new dictionary excluding the 'datetime' key
        cleaned_article = {key: value for key,
                            value in article.items() if key != 'datetime'}
        cleaned_news.append(cleaned_article)

    combined_data = {
            'club': club_info,
            'squad': squad_data,
            'fixtures': fixtures,
            'stats': club_stats,
            'news': cleaned_news
    }

    return combined_data;
