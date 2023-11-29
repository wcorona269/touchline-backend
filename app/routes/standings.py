import json
import os
from flask import Blueprint
import http.client
from dotenv import load_dotenv
load_dotenv(".flaskenv")

api_key = os.getenv("API_KEY")
bp = Blueprint('standings', __name__, url_prefix='/standings')

@bp.route('/<leagueId>', methods=['GET'])
def get_user_info(leagueId):
  conn = http.client.HTTPSConnection("v3.football.api-sports.io")
  headers = {
      'x-rapidapi-host': "v3.football.api-sports.io",
      'x-rapidapi-key': api_key
  }
  
  conn.request("GET",
               f"/standings?league={leagueId}&season=2023",
               headers=headers)
  res = conn.getresponse()
  data = res.read()
  result = data.decode("utf-8")
  json_data = json.loads(result)
  standings = json_data["response"]
  return standings