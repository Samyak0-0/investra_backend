from flask import Blueprint, jsonify
from flask import request
import requests
import os
import json
import datetime

from flask_cors import CORS
from sqlalchemy.orm import sessionmaker
from models.schemas import Portfolio
from models.database import engine


stocks_bp = Blueprint('stocks', __name__, url_prefix="/stocks")

Session = sessionmaker(bind=engine)
CORS(stocks_bp, resources={r"/*": {"origins": "*"}})


@stocks_bp.route('/<symbol>', methods=["GET"])
def get_stock_data(symbol):

    BASE_URL = "https://www.alphavantage.co/query"
    API_KEY = os.environ["API_KEY"]
    interval = request.args.get('interval')

    # Map interval to Alpha Vantage function
    interval_map = {
        'daily': 'TIME_SERIES_DAILY',
        'weekly': 'TIME_SERIES_WEEKLY_ADJUSTED',
        'monthly': 'TIME_SERIES_MONTHLY_ADJUSTED'
    }

    if interval not in interval_map:
        return jsonify({'error': 'Invalid interval. Choose from: daily, weekly, monthly'}), 400

    if (interval == 'daily'):
        params = {
            'function': interval_map[interval],
            'symbol': symbol,
            'apikey': API_KEY,
            'outputsize': 'full'
        }
    else:
        params = {
            'function': interval_map[interval],
            'symbol': symbol,
            'apikey': API_KEY,
        }

    try:
        appdata_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'appdata')
        os.makedirs(appdata_dir, exist_ok=True)
        filename = f"{symbol}_{interval}.json"
        filepath = os.path.join(appdata_dir, filename)

        if os.path.exists(filepath):
            with open(filepath, mode='r', encoding='utf-8') as file:
                data = json.load(file)
            last_api_called_str = data.get("Meta Data", {}).get("6. Last Api Called")
            if last_api_called_str:
                last_api_called = datetime.datetime.strptime(last_api_called_str, "%Y-%m-%d %H:%M:%S")
                now = datetime.datetime.now()
                if (now - last_api_called).total_seconds() < 12 * 3600:
                    print("data returned from appdata")
                    return jsonify(data)
        
        
        print("Fetching data from API")
        response = requests.get(BASE_URL, params=params)
        data = response.json()

        if 'Error Message' in data:
            return jsonify({'error': data['Error Message']}), 400

        if "Meta Data" in data:
            data["Meta Data"]["6. Last Api Called"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Only keep latest 500 daily data points if interval is 'daily'
        if interval == 'daily' and "Time Series (Daily)" in data:
            ts = data["Time Series (Daily)"]
            
            latest_dates = sorted(ts.keys(), reverse=True)[:300]
            filtered_ts = {date: ts[date] for date in latest_dates}
            data["Time Series (Daily)"] = filtered_ts

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print("data returned from api")
        return jsonify(data)
    

    except Exception as e:
        return jsonify({'error': str(e)}), 500



@stocks_bp.route('/add', methods=["POST"])
def post_stock_data():
    data = request.get_json()
    stock_ticker = data.get("stockTicker")
    no_of_stocks = data.get("no_of_Stocks")
    user_id = data.get("userId")

    if not stock_ticker or not no_of_stocks or not user_id:
        return jsonify({"error": "Missing stockTicker, no_of_Stocks or userId"}), 400

    BASE_URL = "https://www.alphavantage.co/query"
    API_KEY = os.environ["API_KEY"]
    interval = 'daily'
    interval_map = 'TIME_SERIES_DAILY'

    params = {
        'function': interval_map,
        'symbol': stock_ticker,
        'apikey': API_KEY,
        'outputsize': 'full'
    }

    session = Session()
    try:
        portfolio = session.query(Portfolio).filter_by(user_id=user_id, stock_name=stock_ticker).first()

        if portfolio:
            portfolio.stock_amt += int(no_of_stocks)
            print("Incrmeented")
        else:
            portfolio = Portfolio(user_id=user_id, stock_name=stock_ticker, stock_amt=int(no_of_stocks))
            session.add(portfolio)
        session.commit()

        appdata_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'appdata')
        os.makedirs(appdata_dir, exist_ok=True)
        filename = f"{stock_ticker}_{interval}.json"
        filepath = os.path.join(appdata_dir, filename)

        if os.path.exists(filepath):
            with open(filepath, mode='r', encoding='utf-8') as file:
                data = json.load(file)
            last_api_called_str = data.get("Meta Data", {}).get("6. Last Api Called")
            if last_api_called_str:
                last_api_called = datetime.datetime.strptime(last_api_called_str, "%Y-%m-%d %H:%M:%S")
                now = datetime.datetime.now()
                if (now - last_api_called).total_seconds() < 12 * 3600:
                    print("data returned from appdata")
                    return jsonify(data)

        print("Fetching data from API")
        response = requests.get(BASE_URL, params=params)
        data = response.json()

        if 'Error Message' in data:
            return jsonify({'error': data['Error Message']}), 400

        if "Meta Data" in data:
            data["Meta Data"]["6. Last Api Called"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if interval == 'daily' and "Time Series (Daily)" in data:
            ts = data["Time Series (Daily)"]
            latest_dates = sorted(ts.keys(), reverse=True)[:300]
            data["Time Series (Daily)"] = {date: ts[date] for date in latest_dates}

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print("data returned from api")
        return jsonify(data)

    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()