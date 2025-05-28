import os
import json
from multiprocessing import Pool, cpu_count
from functools import partial

from db_to_pnd import create_dataframe, get_connection_string
from analyzer_LSTM import extract_product_name
from analyzer_Prophet import run_full_forecast

def forecast_for_product(product_name, df, category_name, market_name, periods):
    try:
        return run_full_forecast(df, product_name, market_name, category_name, periods=periods, json_path=None)
    except Exception as e:
        print(f"✗ {product_name}: {e}")
        return None

def batch_forecast_to_single_file(output_file="Predictions/predicted_products_Prophet.json",
                                  networks=["atb", "silpo"],
                                  categories=None, periods=7):

    # Створення папки Predictions
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    if categories is None:
        categories = [
            "Овочі та фрукти",
            "Молочні продукти та яйця",
            "Хлібобулочні вироби",
            "Напої безалкогольні",
            "Кава та чай"
        ]

    connection_string = get_connection_string()
    all_forecasts = []

    for network in networks:
        print(f"\nМережа: {network}")
        for category_name in categories:
            print(f"\nКатегорія: {category_name}")
            df = create_dataframe(connection_string, network, category_name)
            df['name'] = df['name'].apply(extract_product_name)
            products = sorted(df['name'].unique())

            pool = Pool(processes=cpu_count())
            func = partial(forecast_for_product, df=df, category_name=category_name, market_name=network, periods=periods)
            results = pool.map(func, products)
            pool.close()
            pool.join()

            for res in results:
                if res:
                    all_forecasts.append(res)
                    print(f"  ✓ {res['name']}: {res['price_prediction'][-1]['yhat']:.2f} грн на {res['price_prediction'][-1]['date']}")
                else:
                    print("  ✗ Помилка")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_forecasts, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Збережено {len(all_forecasts)} продуктів у '{output_file}'")

if __name__ == "__main__":
    batch_forecast_to_single_file()
