from flask import request, jsonify
from GoogleNews import GoogleNews
import json
import os
from flask import Blueprint
import http.client
from dotenv import load_dotenv
load_dotenv(".flaskenv")
api_key = os.getenv("API_KEY")

bp = Blueprint('clubs', __name__, url_prefix='/clubs')

headers = {
    'x-rapidapi-host': "v3.football.api-sports.io",
    'x-rapidapi-key': api_key
}

	
@bp.route('/info/<clubId>/<season>', methods=['GET'])
def club_info(clubId, season):
  conn = http.client.HTTPSConnection("v3.football.api-sports.io")
  
  # Request club seasons
  conn.request("GET", f"/teams/seasons?team={clubId}", headers=headers)
  res = conn.getresponse()
  data = res.read()
  result = data.decode("utf-8")
  club_seasons = json.loads(result)['response']
  
  # Request club info
  conn.request("GET", f"/teams?id={clubId}", headers=headers)
  res = conn.getresponse()
  data = res.read()
  result = data.decode("utf-8")
  club_info = json.loads(result)['response']
  
  # Request squad details
  conn.request("GET", f"/players/squads?team={clubId}", headers=headers)
  res = conn.getresponse()
  data = res.read()
  result = data.decode("utf-8")
  squad_data = json.loads(result)['response']
  
  # Request club fixtures (previous and upcoming)
  conn.request("GET", f"/fixtures?team={clubId}&season={season}",headers=headers)
  res = conn.getresponse()
  data = res.read()
  result = data.decode("utf-8")
  fixtures = json.loads(result)['response']
  
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
    conn.request("POST", f"/teams/statistics?team={clubId}&season={season}&league={competition_id}", headers=headers)
    res = conn.getresponse()
    data = res.read()
    result = data.decode("utf-8")
    competition_stats = json.loads(result)['response']
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
    'seasons': club_seasons,
    'stats': club_stats,
    'news': cleaned_news
	}
  
  return combined_data;
