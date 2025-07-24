from flask import Blueprint, jsonify
from flask import request
import requests
import os

news_bp = Blueprint('news', __name__, url_prefix="/news")


@news_bp.route('/<country>/<category>', methods=["GET"])
def get_news_data(country,category):

    BASE_URL = "https://newsapi.org/v2/top-headlines"

    API_NEWS_KEY = os.environ["API_NEWS_KEY"]

    params = {
        'country': country,
        'category': category,
        'apiKey': API_NEWS_KEY
    }

    try:
        response = requests.get(BASE_URL, params=params)
        data = response.json()

        if 'Error Message' in data:
            return jsonify({'error': data['Error Message']}), 400

        return jsonify(data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
