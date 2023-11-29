from flask import Blueprint, request, redirect, jsonify
from GoogleNews import GoogleNews
import random


bp = Blueprint('news', __name__, url_prefix='/news')

@bp.route('/all', methods=['POST'])
def fetchNews():
    try:
        fav_names = request.json.get('favNames', [])
        print(fav_names)
        gNews = GoogleNews(period='10d')
        topics = [
                *fav_names,
                'soccer transfer news',
                'BBC sport football',
                'ESPN FC',
                'Marca',
            ]

        news_articles = []
        for topic in topics:
            gNews.clear()
            gNews.get_news(topic)
            result = gNews.results(sort=True)
            news_articles.extend(result)
            
        random.shuffle(news_articles)

        cleaned_news = []
        for article in news_articles[:100]:
            cleaned_article = {key: value for key, 
                            value in article.items() if key != 'datetime'}
            cleaned_news.append(cleaned_article)

        return cleaned_news;
    except Exception as e:
        # Handle exceptions and return an error response
        return jsonify({'error': str(e)}), 500

@bp.route('/top', methods=['POST'])
def fetchTopNews():
    gNews = GoogleNews(period='2d')
    news_articles = []

    gNews.clear()
    gNews.get_news('soccer news')
    result = gNews.results(sort=True)
    news_articles.extend(result)
    
    max_articles = 10
    count = 0

    cleaned_news = []
    for article in news_articles:
        cleaned_article = {key: value for key, value in article.items() if key != 'datetime'}
        cleaned_news.append(cleaned_article)
        
        count += 1
        if count >= max_articles:
            break

    return cleaned_news;