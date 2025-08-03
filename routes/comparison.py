from flask import Blueprint, jsonify
from flask import request
import requests
import os
import json
import datetime
from models.schemas import User, Portfolio
from models.database import engine
from sqlalchemy.orm import sessionmaker

comparison_bp = Blueprint('comparison', __name__, url_prefix='/comparison')

@comparison_bp.route('/', methods=['GET'])
def get_comparison():

    BASE_URL = "https://www.alphavantage.co/query"
    API_KEY = os.environ["API_KEY"]
    time = request.args.get('time')
    userId = request.args.get('userId')
    
    # Session = sessionmaker(bind=engine)
    # session = Session()
    # user = session.query(User).filter_by(email=mail).first()
    

    window_map = {'30D': 30, '60D': 60, '90D': 90, '1Y': 52, '2Y': 104, '5Y': 260}
    window_size = window_map.get(time, 30)

    TickerList = ['SPY', 'DIA', 'QQQ']

    appdata_dir = os.path.join(os.path.dirname(__file__), '..', 'appdata')
    os.makedirs(appdata_dir, exist_ok=True)

    result = {}

    # Fetch user portfolio if userId is provided
    user_portfolio_normalized = None
    if userId:
        Session = sessionmaker(bind=engine)
        session = Session()
        user_portfolio = session.query(Portfolio).filter_by(user_id=userId).all()
        session.close()
        if user_portfolio:
            # Build a dict: {stock_name: stock_amt}
            portfolio_dict = {p.stock_name: p.stock_amt for p in user_portfolio}
            
            portfolio_series = {}
            for stock, amt in portfolio_dict.items():
                if time in ['1Y', '2Y', '5Y']:
                    filename = f"{stock}_weekly.json"
                    series_key = "Weekly Adjusted Time Series"
                    close_key = "5. adjusted close"
                else:
                    filename = f"{stock}_daily.json"
                    series_key = "Time Series (Daily)"
                    close_key = "4. close"
                filepath = os.path.join(appdata_dir, filename)
                if os.path.exists(filepath):
                    with open(filepath, mode='r', encoding='utf-8') as file:
                        data = json.load(file)
                    time_series = data.get(series_key, {})
                    dates = sorted(time_series.keys(), reverse=True)[:window_size]
                    dates = sorted(dates)
                    closes = [float(time_series[date][close_key]) for date in dates]
                    if len(closes) == window_size:
                        portfolio_series[stock] = (dates, closes, amt)
          
            if portfolio_series:
                
                # print(portfolio_series)

                common_dates = None
                for dates, closes, amt in portfolio_series.values():
                    if common_dates is None:
                        common_dates = set(dates)
                    else:
                        common_dates &= set(dates)
                if common_dates:
                    common_dates = sorted(common_dates)
                    
                    weighted = []
                    
                    for idx, date in enumerate(common_dates):
                        total = 0
                        for stock, (dates, closes, amt) in portfolio_series.items():
                            if date in dates:
                                i = dates.index(date)
                                total += closes[i] * amt
                        weighted.append(total)
                    if weighted:
                        first = weighted[0]
                        user_portfolio_normalized = {date: val/first for date, val in zip(common_dates, weighted)}

    for t in TickerList:
        # Decide file and keys based on time
        if time in ['1Y', '2Y', '5Y']:
            filename = f"{t}_weekly.json"
            series_key = "Weekly Adjusted Time Series"
            close_key = "5. adjusted close"
            api_function = 'TIME_SERIES_WEEKLY_ADJUSTED'
            refresh_hours = 24 * 6  # 6 days
        else:
            filename = f"{t}_daily.json"
            series_key = "Time Series (Daily)"
            close_key = "4. close"
            api_function = 'TIME_SERIES_DAILY'
            refresh_hours = 12  # 12 hours
        filepath = os.path.join(appdata_dir, filename)
        fetch_new = True
        if os.path.exists(filepath):
            with open(filepath, mode='r', encoding='utf-8') as file:
                data = json.load(file)
            meta = data.get("Meta Data", {})
            last_api_called = meta.get("6. Last Api Called")
            if last_api_called:
                try:
                    last_dt = datetime.datetime.strptime(last_api_called, "%Y-%m-%d %H:%M:%S")
                    now = datetime.datetime.now()
                    delta = now - last_dt
                    if delta.total_seconds() < refresh_hours * 3600:
                        fetch_new = False
                except Exception:
                    pass
            else:
                fetch_new = True
        if fetch_new:
            params = {
                'function': api_function,
                'symbol': t,
                'apikey': API_KEY,
                'outputsize': 'compact'
            }
            response = requests.get(BASE_URL, params=params)
            data = response.json()
            if 'Error Message' in data:
                return jsonify({'error': data['Error Message']}), 400
            # Update "6. Last Api Called"
            if "Meta Data" in data:
                data["Meta Data"]["6. Last Api Called"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        time_series = data.get(series_key, {})
        dates = sorted(time_series.keys(), reverse=True)[:window_size]
        # print("\n", dates)
        dates = sorted(dates)
        # print("\n\n",dates)
        
        closes = [float(time_series[date][close_key]) for date in dates]

        if not closes:
            result[t] = {}
            continue
        first = closes[0]

        normalized = {date: round(close/first, 3) for date, close in zip(dates, closes)}
        result[t] = normalized

    # After all index data and user_portfolio_normalized are prepared
    if user_portfolio_normalized:
        # Find common dates between portfolio and all indices
        portfolio_dates = set(user_portfolio_normalized.keys())
        index_dates = None
        for t in TickerList:
            if t in result:
                dates = set(result[t].keys())
                if index_dates is None:
                    index_dates = dates
                else:
                    index_dates &= dates
        if index_dates is not None:
            common_dates = sorted(portfolio_dates & index_dates)
            # Filter all series to only include common dates
            for t in TickerList:
                if t in result:
                    result[t] = {date: result[t][date] for date in common_dates if date in result[t]}
            result['portfolio'] = {date: round(user_portfolio_normalized[date], 3) for date in common_dates if date in user_portfolio_normalized}
        else:
            result['portfolio'] = {date: round(val, 3) for date, val in user_portfolio_normalized.items()}
    return jsonify(result)
