from flask import Blueprint, jsonify
from flask import request
import requests
import os

stocks_bp = Blueprint('stocks', __name__, url_prefix="/stocks")


@stocks_bp.route('/<symbol>', methods=["GET"])
def get_stock_data(symbol):

    BASE_URL = "https://www.alphavantage.co/query"
    API_KEY = os.environ["API_KEY"]
    interval = request.args.get('interval', 'daily')

    # Map interval to Alpha Vantage function
    interval_map = {
        'intraday': 'TIME_SERIES_INTRADAY_ADJUSTED',
        'daily': 'TIME_SERIES_DAILY_ADJUSTED',
        'weekly': 'TIME_SERIES_WEEKLY_ADJUSTED',
        'monthly': 'TIME_SERIES_MONTHLY_ADJUSTED'
    }

    if interval not in interval_map:
        return jsonify({'error': 'Invalid interval. Choose from: intraday, daily, weekly, monthly'}), 400

    params = {
        'function': interval_map[interval],
        'symbol': symbol,
        'apikey': API_KEY
    }

    # Add interval parameter for intraday data
    if interval == 'intraday':
        params['interval'] = '5min'

    try:
        response = requests.get(BASE_URL, params=params)
        data = response.json()

        if 'Error Message' in data:
            return jsonify({'error': data['Error Message']}), 400

        return jsonify(data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
