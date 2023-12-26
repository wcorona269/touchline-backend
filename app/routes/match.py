import json
import os
from flask import Blueprint, jsonify
import http.client
from dotenv import load_dotenv
load_dotenv(".flaskenv")

api_key = os.getenv("API_KEY")

bp = Blueprint('match', __name__, url_prefix='/match')

@bp.route('/<matchId>', methods=['GET'])
def get_match_info(matchId):
  conn = http.client.HTTPSConnection("v3.football.api-sports.io")
  headers = {
      'x-rapidapi-host': "v3.football.api-sports.io",
      'x-rapidapi-key': api_key
  }

  conn.request("GET",
               f"/fixtures?id={matchId}",
               headers=headers)
  res = conn.getresponse()
  data = res.read()
  result = data.decode("utf-8")
  json_data = json.loads(result)
  match = json_data["response"]
  return match
  # if match:
  #   return jsonify({
  #     "message": 'Match fetched successfully',
  #     'match_data': match
  #   }), 200
  # else:
  #   return jsonify({
  #     'message': 'Invalid request data'
  #   }), 401
