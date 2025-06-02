from flask import Flask, jsonify, request
import requests
from datetime import datetime
import os
from dotenv import load_dotenv
from flask_cors import CORS
from models.schemas import User
from models.database import SessionLocal
from signup import signup_bp


app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])
  # Enable CORS for all routes

load_dotenv()

API_KEY = os.getenv("API_KEY") 
BASE_URL = "https://www.alphavantage.co/query"
app.register_blueprint(signup_bp)

@app.route('/api/stock/<symbol>', methods=['GET'])
def get_stock_data(symbol):
    interval = request.args.get('interval', 'daily')
    
    # Map interval to Alpha Vantage function
    interval_map = {
        'intraday': 'TIME_SERIES_INTRADAY',
        'daily': 'TIME_SERIES_DAILY',
        'weekly': 'TIME_SERIES_WEEKLY',
        'monthly': 'TIME_SERIES_MONTHLY'
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

if __name__ == '__main__':
    app.run(debug=True)
