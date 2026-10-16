from flask import request
import logging
import json
import math
from datetime import datetime
import os
from flask import Blueprint, jsonify
import http.client
from dotenv import load_dotenv
from GoogleNews import GoogleNews
from .league_ids import get_league_ids
from ..extensions import cache
from .api_football import api_get, is_success, ApiFootballError

load_dotenv(".flaskenv")
api_key = os.getenv("API_KEY")

bp = Blueprint('league', __name__, url_prefix='/leagues')

@bp.route('/index', methods=['GET'])
@cache.cached(timeout=3600)
def fetchAllComps():
    ids = get_league_ids()
    
    conn = http.client.HTTPSConnection("v3.football.api-sports.io")
    headers = {
            'x-rapidapi-host': "v3.football.api-sports.io",
            'x-rapidapi-key': api_key
    }
    
    # Make the first API call to get standings
    league_data = api_get(f"/leagues?current=True", conn)
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
    conn = http.client.HTTPSConnection("v3.football.api-sports.io")
    headers = {
                'x-rapidapi-host': "v3.football.api-sports.io",
                'x-rapidapi-key': api_key
        }

    # Make the first API call to get standings
    standings_data = api_get(f"/standings?league={leagueId}&season={season}", conn)

    # Get top scorer data
    top_scorer_data = api_get(f"/players/topscorers?season={season}&league={leagueId}", conn)

    # Top assists data
    top_assists_data = api_get(f"/players/topassists?season={season}&league={leagueId}", conn)

    # Fixture data
    fixture_data = api_get(f"/fixtures?season={season}&league={leagueId}", conn)

    # fetch competition news
    country = standings_data[0]['league']['country']
    name = standings_data[0]['league']['name']
    news_topic = f'{country} {name}'
    gNews = GoogleNews(period='20d')
    gNews.get_news(news_topic)
    competition_news = gNews.results()

    cleaned_news = []
    for article in competition_news:
        # Create a new dictionary excluding the 'datetime' key
        cleaned_article = {key: value for key,
                        value in article.items() if key != 'datetime'}
        cleaned_news.append(cleaned_article)
            
    # combine data and return to frontend
    combined_data = {
            "standings": standings_data,
            "top scorers": top_scorer_data,
            "top assists": top_assists_data,
            "fixtures": fixture_data,
            "news": cleaned_news,
    }

    return combined_data