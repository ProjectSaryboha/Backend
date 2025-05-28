import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import json
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Input, LSTM, Dense

def extract_product_name(full_name: str):
    import re
    match = re.search(r"^(.*?)\s*купити", full_name, re.IGNORECASE)
    if match:
        name = match.group(1)
    else:
        words = full_name.split()
        name = ' '.join(words[:3])
    clean_name = re.sub(r'[^\w\s]', '', name).strip()
    return clean_name

def create_dataset(data, look_back=10):
    X, y = [], []
    for i in range(len(data) - look_back):
        X.append(data[i:i+look_back])
        y.append(data[i+look_back])
    return np.array(X), np.array(y)

def prepare_product_data(df, product_name, look_back=2):
    product_df = df[df['name'] == product_name].copy()
    product_df = product_df.sort_values('timestamp')
    product_df.set_index('timestamp', inplace=True)
    product_df = product_df['price'].resample('D').mean()
    product_df = product_df.interpolate()

    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_prices = scaler.fit_transform(product_df.values.reshape(-1, 1))

    X, y = create_dataset(scaled_prices, look_back)
    return X, y, scaler, scaled_prices, product_df

def build_and_train_model(X, y, epochs=20, batch_size=16, verbose=0):
    model = Sequential()
    model.add(Input(shape=(X.shape[1], X.shape[2])))
    model.add(LSTM(20))
    model.add(Dense(1))
    model.compile(loss='mean_squared_error', optimizer='adam')
    model.fit(X, y, epochs=epochs, batch_size=batch_size, validation_split=0.1, verbose=verbose)
    return model

def predict_next_day_price(model, scaler, scaled_prices, look_back=2):
    last_sequence = scaled_prices[-look_back:]
    last_sequence = last_sequence.reshape((1, look_back, 1))
    predicted_scaled = model.predict(last_sequence)
    predicted_price = scaler.inverse_transform(predicted_scaled)
    return predicted_price[0][0]

def run_full_prediction(df, product_name, category, market, look_back=2, epochs=50, batch_size=16, json_path=None):
    X, y, scaler, scaled_prices, price_history_series = prepare_product_data(df, product_name, look_back)
    if len(X) == 0:
        raise ValueError("Недостатньо даних для передбачення")

    model = build_and_train_model(X, y, epochs=epochs, batch_size=batch_size, verbose=0)
    predicted_price = predict_next_day_price(model, scaler, scaled_prices, look_back)

    price_history = [
        {"date": date.strftime('%Y-%m-%d'), "price": float(price)}
        for date, price in price_history_series.items()
    ]

    result = {
        "name": product_name,
        "category": category,
        "market": market,
        "price_history": price_history,
        "predicted_price": float(predicted_price)
    }

    if json_path:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)

    return result
