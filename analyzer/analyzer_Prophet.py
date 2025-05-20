import json
import pandas as pd
from prophet import Prophet

def prepare_prophet_data(df, product_name):
    product_df = df[df['name'] == product_name].copy()
    product_df = product_df.sort_values('timestamp')
    product_df.set_index('timestamp', inplace=True)
    daily_prices = product_df['price'].resample('D').mean().interpolate()

    prophet_df = daily_prices.reset_index().rename(columns={'timestamp': 'ds', 'price': 'y'})
    prophet_df['ds'] = prophet_df['ds'].dt.tz_localize(None)
    return prophet_df, daily_prices

def forecast_with_prophet(prophet_df, periods=7):
    model = Prophet(daily_seasonality=True)
    model.fit(prophet_df)
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)
    return forecast

def run_full_forecast(df, product_name, category, periods=7, json_path=None):
    prophet_df, daily_prices = prepare_prophet_data(df, product_name)
    if prophet_df.shape[0] < 5:
        raise ValueError("Недостатньо даних для передбачення")
    
    forecast = forecast_with_prophet(prophet_df, periods)

    price_history = [
        {"date": date.strftime('%Y-%m-%d'), "price": float(price)}
        for date, price in daily_prices.items()
    ]

    forecast_data = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(periods)
    predictions = []
    for _, row in forecast_data.iterrows():
        predictions.append({
            "date": row['ds'].strftime('%Y-%m-%d'),
            "yhat": round(float(row['yhat']), 2),
            "yhat_lower": round(float(row['yhat_lower']), 2),
            "yhat_upper": round(float(row['yhat_upper']), 2)
        })

    result = {
        "name": product_name,
        "category": category,
        "price_history": price_history,
        "price_prediction": predictions
    }

    if json_path:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)

    return predictions
