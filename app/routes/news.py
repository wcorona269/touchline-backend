from flask import Blueprint, request, redirect, jsonify
from GoogleNews import GoogleNews
import random

bp = Blueprint('news', __name__, url_prefix='/news')

@bp.route('/all', methods=['POST'])
def fetchNews():
    try:
        fav_names = request.json.get('favNames', []) if request.json else []
        fav_names = []
        gNews = GoogleNews(period='10d')
        num_to_select = min(len(fav_names), 3)
        random_faves = random.sample(fav_names, num_to_select)
        topics = [
                *random_faves,
                'soccer transfer news',
                'BBC sport football',
                'ESPN FC',
            ]
        
        news_articles = []
        for topic in topics:
            gNews.clear()
            gNews.search(topic)
            result = gNews.results(sort=True)
            news_articles.extend(result)
            
        random.shuffle(news_articles)
        cleaned_news = []
        for article in news_articles[:100]:
            cleaned_article = {key: value for key, 
                            value in article.items() if key != 'datetime'}
            cleaned_news.append(cleaned_article)
        return jsonify({
            'message': 'News fetched successfully',
            'news': cleaned_news,
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/top', methods=['POST'])
def fetchTopNews():
    try:
        gNews = GoogleNews()
        gNews.set_lang('en')
        gNews.set_period('7d')
        news_articles = []
        # gNews.clear()
        print(gNews.getVersion())
        gNews.search('soccer news')
        result = gNews.results()
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

        return jsonify({
            'message': 'News fetched successfully',
            'news': cleaned_news,
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500