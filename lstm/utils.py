import pandas as pd
import numpy as np

from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt


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
