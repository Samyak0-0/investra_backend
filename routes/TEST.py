from flask import Blueprint, jsonify
from flask import request
import requests
import os
import json
from models.schemas import User, Portfolio
from models.database import engine
from sqlalchemy.orm import sessionmaker

comparison_bp = Blueprint('comparison', __name__, url_prefix='/comparison')

@comparison_bp.route('/', methods=['GET'])
def get_comparison():
    
    BASE_URL = "https://www.alphavantage.co/query"
    API_KEY = os.environ["API_KEY"]
    
    time = request.args.get('time')
    print(time)
    
    # Session = sessionmaker(bind=engine)
    # session = Session()
    # user = session.query(User).filter_by(email=mail).first()
    
    # if user:
    #     portfolios = session.query(Portfolio).filter_by(user_id=user.id).all()
    #     session.close()
    #     data = None;
    #     totalValue = 0;
    #     totalSecondPrice = 0;
    #     closing_price_list = []
    #     second_price_list = []
        
    TickerList = ['SPY', 'DIA', 'QQQ']
    time_series_function = ['TIME_SERIES_DAILY', 'TIME_SERIES_WEEKLY_ADJUSTED', 'TIME_SERIES_MONTHLY']
    time_Series = ['daily', 'weekly', 'monthly']
 
    appdata_dir = os.path.join(os.path.dirname(__file__), '..', 'appdata')
    os.makedirs(appdata_dir, exist_ok=True)
    
    match time:
        case '30D':
            print(time)
        case '60D':
            print(time)
        case '90D':
            print(time)

    
        case '1Y':
            print(time)
        case '2Y':
            print(time)
        case '5Y':
            print(time)
    
    for t in TickerList:
        filename = f"{t}_daily.json"
        filepath = os.path.join(appdata_dir, filename)
        

        if os.path.exists(filepath):
            with open(filepath, mode='r', encoding='utf-8') as file:
                data = json.load(file)
            # print("data returned from appdata")
            # return jsonify(data)
        else:
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': t,
                'apikey': API_KEY,
                'outputsize': 'compact'
            }
            response = requests.get(BASE_URL, params=params)
            data = response.json()

            if 'Error Message' in data:
                return jsonify({'error': data['Error Message']}), 400;
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2);
            
            
            time_series = data["Time Series (Daily)"]
            dates = sorted(time_series.keys(), reverse=True)
            
            # last_refreshed = data["Meta Data"]["3. Last Refreshed"]
            # first_date = dates[0]
            # closing_price = data["Time Series (Daily)"][first_date]["4. close"]
            # closing_price_list.append(closing_price)
            
            
            # second_date = dates[1]
            # second_closing_price = time_series[second_date]["4. close"]
            # second_price_list.append(second_closing_price)
            
            # totalValue += float(closing_price)*int(p.stock_amt);
            # totalSecondPrice += float(second_closing_price)*int(p.stock_amt);
            
            # print(f"Most recent closing price: ${closing_price}")
                # print("data returned from api")
                # return jsonify(data);
                
                
                
    return jsonify("dfghj")
            
    # else:
    # session.close()
    # return jsonify({"error": "User not found"}), 404
