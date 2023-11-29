import json
import os
from flask import Blueprint
import http.client
from dotenv import load_dotenv
load_dotenv(".flaskenv")
api_key = os.getenv("API_KEY")

bp = Blueprint('players', __name__, url_prefix='/players')

@bp.route('/<playerId>', methods=['GET'])
def competitionInfo(playerId):
  conn = http.client.HTTPSConnection("v3.football.api-sports.io")
  headers = {
      'x-rapidapi-host': "v3.football.api-sports.io",
      'x-rapidapi-key': api_key
  }

  # Request club info
  conn.request("GET", f"/players?id={playerId}&season=2023", headers=headers)
  res = conn.getresponse()
  data = res.read()
  result = data.decode("utf-8")
  player_data = json.loads(result)['response']
  return player_data