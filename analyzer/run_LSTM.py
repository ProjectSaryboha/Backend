import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import json
from multiprocessing import Pool, cpu_count
from functools import partial

from analyzer.db_to_pnd import create_dataframe, get_connection_string
from analyzer.analyzer_LSTM import extract_product_name, run_full_prediction

def predict_for_product(product_name, df, category_name, market_name, look_back, epochs, batch_size):
    try:
        return run_full_prediction(
            df, product_name, category_name, market_name,
            look_back=look_back, epochs=epochs, batch_size=batch_size,
            json_path=None
        )
    except Exception as e:
        print(f"✗ {product_name}: {e}")
        return None

def batch_predict_all_categories(output_file="Predictions/predicted_products_LSTM.json",
                              networks=["atb", "silpo"],
                              categories=None, look_back=2, epochs=20, batch_size=16):

    # Створити папку Predictions
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
    all_predictions = []

    for network in networks:
        print(f"\nМережа: {network}")
        for category_name in categories:
            print(f"\nКатегорія: {category_name}")
            df = create_dataframe(connection_string, network, category_name)
            df['name'] = df['name'].apply(extract_product_name)
            products = sorted(df['name'].unique())

            pool = Pool(processes=cpu_count())
            func = partial(predict_for_product, df=df, category_name=category_name, market_name=network, 
                           look_back=look_back, epochs=epochs, batch_size=batch_size)
            results = pool.map(func, products)
            pool.close()
            pool.join()

            for res in results:
                if res:
                    all_predictions.append(res)
                    print(f"  ✓ {res['name']}: {res['predicted_price']:.2f} грн")
                else:
                    print("  ✗ Помилка")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_predictions, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Збережено {len(all_predictions)} продуктів у '{output_file}'")

if __name__ == "__main__":
    batch_predict_all_categories()