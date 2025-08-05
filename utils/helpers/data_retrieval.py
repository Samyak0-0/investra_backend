import requests
import os
from datetime import timedelta
import json


def load_cached_data(save_dir: str, _def_fname: str) -> dict:
    try:
        with open(f'{save_dir}{_def_fname}', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Exception occured: {e}")


def fetch_data(**kwargs) -> dict:
    NEWS_API_KEY = os.getenv('API_NEWS_KEY')
    if not NEWS_API_KEY:
        raise ValueError("NEWS_API_KEY environment variable not set")

    ticker = kwargs.get('ticker')
    if not ticker:
        raise ValueError("Ticker not provided")

    save_dir = "./news_data/"
    _def_fname = f"{ticker.lower()}_data.json"

    EVERYTHING_ENDPOINT_URI = f'https://newsapi.org/v2/everything?q={ticker}&apiKey={NEWS_API_KEY}'

    try:
        cache_path = f'{save_dir}{_def_fname}'
        if os.path.exists(cache_path):
            print(f"Using cached data for {ticker}")
            return load_cached_data(save_dir=save_dir, _def_fname=_def_fname)
        else:
            print(f"Fetching fresh data for {ticker}")
            result = requests.get(EVERYTHING_ENDPOINT_URI)
            result.raise_for_status()
            save_json_to_file(
                result.json(), filename=_def_fname, save_dir=save_dir)
            print(result.json())
            return result.json()
    except Exception as e:
        print(f"Exception: {e}")


def save_json_to_file(data, filename="app_data.json", save_dir="./news_data/"):
    try:
        os.makedirs(save_dir, exist_ok=True)
        with open(os.path.join(save_dir, filename), 'w') as f:
            json.dump(data, f, indent=4)
        print(f"JSON Data saved to {os.path.join(save_dir, filename)}")
    except Exception as e:
        print(f"Exception occurred: {e}")


def return_titles(json_data):
    titles = []
    articles = json_data.get('articles', [])
    for article in articles:
        if article and 'title' in article:
            titles.append(article['title'])
    return titles
