
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
import os
from dotenv import load_dotenv
# from lstm.utils import fetch_stock_data, preprocess_data
import numpy as np
import requests
import pandas as pd
from flask import jsonify

load_dotenv(override=True)  # take environment variables from .env file

API_KEY = os.getenv('API_KEY')

def predict(days, symbol, API_KEY = API_KEY):
    model = load_model(f"models/{symbol.upper()}_model.h5")
    # data = fetch_stock_data(symbol, API_KEY)
    # df = preprocess_data(data)
    # time_step= 100
    # scaler = MinMaxScaler(feature_range=(0, 1))
    # scaled_data = scaler.fit_transform(df.reshape(-1, 1))


    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=compact&apikey={API_KEY}"
    r = requests.get(url)
    data = r.json()
    if "Time Series (Daily)" not in data:
        return {"error": f"Invalid response: {data}"}

    data = data["Time Series (Daily)"]
    # Convert to DataFrame
    df = pd.DataFrame(data).T
    df = df.astype(float)
    df = df.sort_index()  # oldest to newest
    close_prices = df["4. close"].values

    time_step = 100
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(close_prices.reshape(-1, 1))

    # Last 100 prices for LSTM input
    temp_input = list(scaled_data[-time_step:].flatten())
    predicted_prices = []

    for i in range(days):
        # Take last n_steps as input
        x_input = np.array(temp_input[-time_step:]).reshape((1, time_step, 1))

        # Predict next price
        yhat = model.predict(x_input, verbose=0)
        
        # Append prediction
        temp_input.append(yhat[0][0])
        predicted_prices.append(yhat[0][0])
    
    predicted_prices = scaler.inverse_transform(np.array(predicted_prices).reshape(-1, 1))


    return jsonify(predicted_prices.tolist())


