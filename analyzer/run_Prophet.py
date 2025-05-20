import os
from multiprocessing import Pool, cpu_count
from functools import partial
from db_to_pnd import create_dataframe, get_connection_string
from analyzer_LSTM import extract_product_name
from analyzer_Prophet import run_full_forecast

def forecast_for_product(product_name, df, category_name, category_dir, periods):
    try:
        json_path = os.path.join(category_dir, f"{product_name.replace(' ', '_')}_Prophet_schema.json")
        if os.path.exists(json_path):
            return f"✓ Пропущено (вже існує): {product_name}"

        predictions = run_full_forecast(df, product_name, category_name, periods=periods, json_path=json_path)
        return f"✓ {product_name}: {predictions[-1]['yhat']:.2f} грн (на {predictions[-1]['date']})"
    except Exception as e:
        return f"✗ {product_name}: {e}"

def batch_forecast_all_categories(base_dir="predictions", networks=["atb", "silpo"],
                                  categories=None, periods=7):
    if categories is None:
        categories = [
            "Овочі та фрукти",
            "Молочні продукти та яйця",
            "Хлібобулочні вироби",
            "Напої безалкогольні",
            "Кава та чай"
        ]

    connection_string = get_connection_string()

    for network in networks:
        print(f"\nМережа: {network}")
        for category_name in categories:
            print(f"\nКатегорія: {category_name}")
            df = create_dataframe(connection_string, network, category_name)
            df['name'] = df['name'].apply(extract_product_name)
            products = sorted(df['name'].unique())

            category_dir = os.path.join(base_dir, network, category_name.replace(' ', '_'))
            os.makedirs(category_dir, exist_ok=True)

            pool = Pool(processes=cpu_count())
            func = partial(forecast_for_product, df=df, category_name=category_name,
                           category_dir=category_dir, periods=periods)
            results = pool.map(func, products)
            pool.close()
            pool.join()

            for res in results:
                print("  ", res)

if __name__ == "__main__":
    batch_forecast_all_categories(base_dir="predictions_Prophet")
