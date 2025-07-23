from flask import Blueprint, jsonify
from flask import request
import requests
import os
import json
from models.schemas import User, Portfolio
from models.database import engine
from sqlalchemy.orm import sessionmaker
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64


simulation_bp = Blueprint('simulation', __name__, url_prefix='/simulation')

@simulation_bp.route('/', methods=['GET'])
def get_simulation():
    
    BASE_URL = "https://www.alphavantage.co/query"
    API_KEY = os.environ["API_KEY"]
    simulationsNumber = int(request.args.get('simulations'))
    timeHorizon = int(request.args.get('timeHorizon'))
    confLevel = int(request.args.get('confLevel'))
    userId = request.args.get('userId')
    
    appdata_dir = os.path.join(os.path.dirname(__file__), '..', 'appdata')
    os.makedirs(appdata_dir, exist_ok=True)
    print("WHAT DA HELL")
    data = None;

    if userId:
        
        userDataPath = os.path.join(appdata_dir, "userPortfolios", f"{userId}.json")
        os.makedirs(os.path.dirname(userDataPath), exist_ok=True)  # Ensure userPortfolios dir exists

        
        if os.path.exists(userDataPath):
            with open(userDataPath, mode='r', encoding='utf-8') as file:
                data = json.load(file)
        else:
            Session = sessionmaker(bind=engine)
            session = Session()
            user_portfolio = session.query(Portfolio).filter_by(user_id=userId).all()
            session.close()
            
            if user_portfolio:
                portfolio_dict = {p.stock_name: p.stock_amt for p in user_portfolio}
                portfolio_series = {}

                for stock, amt in portfolio_dict.items():
                    filename = f"{stock}_daily.json"
                    filepath = os.path.join(appdata_dir, filename)
                    if os.path.exists(filepath):
                        with open(filepath, mode='r', encoding='utf-8') as file:
                            stock_data = json.load(file)
                        series_key = "Time Series (Daily)"
                        close_key = "4. close"
                        if series_key in stock_data:
                            dates = []
                            closes = []
                            for date, daily_data in stock_data[series_key].items():
                                dates.append(date)
                                closes.append(float(daily_data[close_key]))
                            portfolio_series[stock] = (dates, closes, amt)

                # Find common dates across all stocks
                common_dates = None
                for dates, closes, amt in portfolio_series.values():
                    if common_dates is None:
                        common_dates = set(dates)
                    else:
                        common_dates &= set(dates)
                if common_dates:
                    common_dates = sorted(common_dates)
                    portfolio_values = {}
                    for date in common_dates:
                        total = 0
                        for stock, (dates, closes, amt) in portfolio_series.items():
                            if date in dates:
                                i = dates.index(date)
                                total += closes[i] * amt
                        portfolio_values[date] = round(total, 3)

                    #Save to user portfolio file
                    with open(userDataPath, mode='w', encoding='utf-8') as file:
                        json.dump(portfolio_values, file, indent=2)

                    data = jsonify(portfolio_values)  

        # return data;
        
        dates = sorted(data.keys())
        values = [data[date] for date in dates]
        
         # 2. Calculate daily returns in percentage
        values = np.array(values)
        if len(values) < 2:
            return jsonify({"error": "Not enough data for simulation"}), 400
        returns = values[1:] / values[:-1] - 1
        # print("returns: ", returns)

        n_simulations = simulationsNumber
        n_days = timeHorizon
        last_value = values[-1]
        simulations = np.zeros((n_simulations, n_days))
        for i in range(n_simulations):
            simulated_returns = np.random.choice(returns, size=n_days, replace=True)
            simulated_path = [last_value]
            for r in simulated_returns:
                simulated_path.append(simulated_path[-1] * (1 + r))
            simulations[i] = simulated_path[1:]

        final_values = simulations[:, -1]
        mean_final = np.mean(final_values)
        median_final = np.median(final_values)
        p5 = np.percentile(final_values, 100-confLevel)
        p95 = np.percentile(final_values, confLevel)
        prob_loss = np.mean(final_values < last_value)

        # Plot all simulation paths (or a sample if too many) with random colors
        plt.figure(figsize=(10, 6))
        np.random.seed(42)  # For reproducibility of colors
        for i in range(min(100, n_simulations)):  # Plot up to 100 paths for clarity
            color = np.random.rand(3,)  # Random RGB color
            plt.plot(simulations[i], color=color, alpha=0.5)
        plt.title('Simulated Portfolio Value Paths')
        plt.xlabel('Days')
        plt.ylabel('Portfolio Value')
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        paths_img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()

        # Plot histogram of final values
        plt.figure(figsize=(8, 5))
        plt.hist(final_values, bins=30, color='green', alpha=0.7)
        plt.title('Distribution of Final Portfolio Values')
        plt.xlabel('Final Portfolio Value')
        plt.ylabel('Frequency')
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        hist_img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()

        # Find the most probable path (closest to median final value)
        median_idx = np.argmin(np.abs(final_values - median_final))
        most_probable_path = simulations[median_idx]

        # Plot the most probable path
        plt.figure(figsize=(10, 6))
        plt.plot(most_probable_path, color='red', label='Most Probable Path')
        plt.title('Most Probable Portfolio Value Path')
        plt.xlabel('Days')
        plt.ylabel('Portfolio Value')
        plt.legend()
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        most_probable_img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()

        result = {
            "mean_final_value": round(mean_final, 2),
            "median_final_value": round(median_final, 2),
            "5th_percentile": round(p5, 2),
            "95th_percentile": round(p95, 2),
            "probability_of_loss": round(prob_loss, 3),
            "last_value": round(last_value, 2)
        }
        result['paths_plot'] = f"data:image/png;base64,{paths_img_base64}"
        result['histogram'] = f"data:image/png;base64,{hist_img_base64}"
        result['most_probable_path_plot'] = f"data:image/png;base64,{most_probable_img_base64}"
        
        return jsonify(result)

