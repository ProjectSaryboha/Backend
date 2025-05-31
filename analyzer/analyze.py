import os
import pandas as pd
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)

# DEFAULT_JSON = os.path.join(PARENT_DIR, "Predictions", "predicted_products_LSTM.json")

def get_input_file_by_model(model):
    model = (model or "lstm").lower()
    if model == "prophet":
        return os.path.join(PARENT_DIR, "Predictions", "predicted_products_Prophet.json")
    return os.path.join(PARENT_DIR, "Predictions", "predicted_products_LSTM.json")

def load_dataframe(input_file, model):
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
    except Exception as e:
        print(f"Помилка при читанні файлу: {e}")
        return pd.DataFrame()

    if model == "prophet":
        records = []
        for item in raw_data:
            if not isinstance(item, dict):
                continue
            prediction_list = item.get("price_prediction", [])
            if prediction_list and isinstance(prediction_list, list):
                last_forecast = prediction_list[-1]
                predicted_price = last_forecast.get("yhat")

                if predicted_price is not None:
                    records.append({
                        "name": item.get("name"),
                        "category": item.get("category"),
                        "market": item.get("market"),
                        "predicted_price": predicted_price,
                        "price_history": item.get("price_history", [])
                    })
        return pd.DataFrame(records)

    return pd.DataFrame(raw_data)


def get_products_by_price(category, market=None, model=None):
    input_file = get_input_file_by_model(model)
    df = load_dataframe(input_file, model)

    required_columns = ['category', 'predicted_price', 'market', 'name']
    if not all(col in df.columns for col in required_columns):
        print(f"У даних немає потрібних колонок {required_columns}")
        return []

    df = df[pd.to_numeric(df['predicted_price'], errors='coerce').notnull()]
    df['predicted_price'] = df['predicted_price'].astype(float)

    filtered = df[df['category'] == category]
    if market:
        filtered = filtered[filtered['market'] == market]

    if filtered.empty:
        print(f"Категорію '{category}'{f' у мережі {market}' if market else ''} не знайдено.")
        return []

    sorted_products = filtered.sort_values(by='predicted_price', ascending=True)

    return sorted_products[['name', 'predicted_price']].to_dict(orient='records')

def get_top_5_expensive_products(market=None, model=None):
    input_file = get_input_file_by_model(model)
    df = load_dataframe(input_file, model)

    if 'predicted_price' not in df.columns:
        print("У даних немає колонки 'predicted_price'")
        return []

    df = df[pd.to_numeric(df['predicted_price'], errors='coerce').notnull()]
    df['predicted_price'] = df['predicted_price'].astype(float)

    if market:
        df = df[df['market'] == market]

    if df.empty:
        print(f"Немає товарів для мережі '{market}'")
        return []

    top_5 = df.sort_values(by='predicted_price', ascending=False).head(5)

    required_columns = ['name', 'predicted_price', 'price_history']
    for col in required_columns:
        if col not in top_5.columns:
            print(f"У даних немає колонки '{col}'")
            return []

    return top_5[required_columns].to_dict(orient='records')

def get_categories_sorted_by_average_price(market=None, model=None):
    input_file = get_input_file_by_model(model)
    df = load_dataframe(input_file, model)

    if 'predicted_price' not in df.columns or 'category' not in df.columns:
        print("У даних немає потрібних колонок 'predicted_price' або 'category'")
        return []

    df = df[pd.to_numeric(df['predicted_price'], errors='coerce').notnull()]
    df['predicted_price'] = df['predicted_price'].astype(float)

    if market:
        df = df[df['market'] == market]

    if df.empty:
        print(f"Немає даних для мережі '{market}'")
        return []

    avg_prices = df.groupby('category')['predicted_price'].mean().reset_index()
    avg_prices = avg_prices.sort_values(by='predicted_price', ascending=False)

    result = []
    for _, row in avg_prices.iterrows():
        category = row['category']
        price = row['predicted_price']
        sample = df[df['category'] == category].iloc[0]
        result.append({
            'category': category,
            'predicted_price': price,
            'price_history': sample.get('price_history', [])
        })

    return result

def get_product_counts_by_category(market=None, model=None):
    input_file = get_input_file_by_model(model)
    df = load_dataframe(input_file, model)

    if 'category' not in df.columns:
        print("У даних немає колонки 'category'")
        return []

    if market:
        df = df[df['market'] == market]

        if df.empty:
            print(f"Товарів мережі '{market}' не знайдено.")
            return []

    category_counts = df['category'].value_counts().reset_index()
    category_counts.columns = ['category', 'count']

    return category_counts.to_dict(orient='records')