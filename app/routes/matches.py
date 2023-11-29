import json
import os
from flask import Blueprint, jsonify
import http.client
from dotenv import load_dotenv
from .league_ids import get_league_ids
load_dotenv(".flaskenv")

api_key = os.getenv("API_KEY")

bp = Blueprint('matches', __name__, url_prefix='/matches')

@bp.route('/<date>', methods=['GET'])
def matches(date):
    conn = http.client.HTTPSConnection("v3.football.api-sports.io")
    headers = {
    'x-rapidapi-host': "v3.football.api-sports.io",
    'x-rapidapi-key': api_key
    }

    conn.request("GET",
                f"/fixtures?date={date}",
                headers=headers)
    res = conn.getresponse()
    data = res.read()
    result = data.decode("utf-8")
    json_data = json.loads(result)
    matches_of_the_day = json_data["response"]
    
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
    conn = http.client.HTTPSConnection("v3.football.api-sports.io")
    headers = {
        'x-rapidapi-host': "v3.football.api-sports.io",
        'x-rapidapi-key': api_key
    }

    conn.request("GET", "/fixtures?live=all",headers=headers)
    res = conn.getresponse()
    data = res.read()
    result = data.decode("utf-8")
    json_data = json.loads(result)
    live_matches = json_data["response"]
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
