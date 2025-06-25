from flask import Blueprint, jsonify
from flask import request
import requests
import os
import json

stocks_bp = Blueprint('stocks', __name__, url_prefix="/stocks")


@stocks_bp.route('/<symbol>', methods=["GET"])
def get_stock_data(symbol):

    BASE_URL = "https://www.alphavantage.co/query"
    API_KEY = os.environ["API_KEY"]
    interval = request.args.get('interval', 'daily')

    # Map interval to Alpha Vantage function
    interval_map = {
        'daily': 'TIME_SERIES_DAILY',
        'weekly': 'TIME_SERIES_WEEKLY_ADJUSTED',
        'monthly': 'TIME_SERIES_MONTHLY_ADJUSTED'
    }

    if interval not in interval_map:
        return jsonify({'error': 'Invalid interval. Choose from: intraday, daily, weekly, monthly'}), 400

    if (interval == 'daily'):
        params = {
            'function': interval_map[interval],
            'symbol': symbol,
            'apikey': API_KEY,
            'outputsize': 'compact'
        }
    else:
        params = {
            'function': interval_map[interval],
            'symbol': symbol,
            'apikey': API_KEY,
        }

    # Add interval parameter for intraday data
    if interval == 'intraday':
        params['interval'] = '5min'

    try:
        appdata_dir = os.path.join(os.path.dirname(__file__), '..', 'appdata')
        os.makedirs(appdata_dir, exist_ok=True)
        filename = f"{symbol}_{interval}.json"
        filepath = os.path.join(appdata_dir, filename)

        if os.path.exists(filepath):
            with open(filepath, mode='r', encoding='utf-8') as file:
                data = json.load(file)
            print("data returned from appdata")
            return jsonify(data)
        else:
            response = requests.get(BASE_URL, params=params)
            data = response.json()

            if 'Error Message' in data:
                return jsonify({'error': data['Error Message']}), 400;
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2);
            
            print("data returned from api")
            return jsonify(data);
        

    except Exception as e:
        return jsonify({'error': str(e)}), 500
