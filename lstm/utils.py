import pandas as pd
import numpy as np
import os
import requests
from sklearn.preprocessing import MinMaxScaler


def scale_data(df):
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(np.array(df).reshape(-1, 1))
    return scaled_data

def split_data(data):
  training_size = int(len(data)*0.8)
  test_size = len(data) - training_size

  train_data = data[0:training_size, :]
  test_data = data[training_size:len(data), :1]

  return train_data, test_data, training_size, test_size

def create_dataset(dataset, time_step=1):
	dataX, dataY = [], []
	for i in range(len(dataset)-time_step- 1):
		a = dataset[i:(i+time_step), 0]
		dataX.append(a)
		dataY.append(dataset[i + time_step, 0])
	return np.array(dataX), np.array(dataY)


def fetch_stock_data(symbol, api_key):
    url = (
        f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY'
        f'&symbol={symbol}&apikey={api_key}&outputsize=full&datatype=csv'
    )
    df = pd.read_csv(url)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.sort_values('timestamp', inplace=True)
    return df.reset_index(drop=True)


def preprocess_data(df):
    data = df['close'].dropna().values
    return data



def ensure_stock_data(symbol: str, api_key: str):
    symbol_upper = symbol.upper()
    appdata_dir = os.path.join(os.path.dirname(__file__),'..','appdata')

    file_path = os.path.join(appdata_dir, f'{symbol_upper}_daily.json')

    if os.path.exists(file_path):
        print(f"[INFO] Using cached data: {file_path}")
        return file_path
    
    url = (
        f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY"
        f"&symbol={symbol_upper}&apikey={api_key}&output=compact"
    )
    print(f'[INFO] Fetching {symbol_upper} data from Alpha Vantage...')
    response = requests.get(url)
    data = response.json()

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print('[INFO] Data saved to {file_path}')

    return file_path