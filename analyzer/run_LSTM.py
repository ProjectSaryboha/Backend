import os
from multiprocessing import Pool, cpu_count
from functools import partial
from db_to_pnd import create_dataframe, get_connection_string
from analyzer_LSTM import extract_product_name, run_full_prediction

def predict_for_product(product_name, df, category_name, category_dir, look_back, epochs, batch_size):
    try:
        json_path = os.path.join(category_dir, f"{product_name.replace(' ', '_')}_LSTM_schema.json")
        
        # Якщо результат вже існує — пропускаємо
        if os.path.exists(json_path):
            return f"✓ Пропущено (вже існує): {product_name}"

        predicted_price = run_full_prediction(
            df, product_name, category_name,
            look_back=look_back, epochs=epochs, batch_size=batch_size,
            json_path=json_path
        )
        return f"✓ {product_name}: {predicted_price:.2f} грн"
    except Exception as e:
        return f"✗ {product_name}: {e}"

def batch_predict_all_categories(base_dir="predictions_LSTM", networks=["atb", "silpo"],
                                  categories=None, look_back=2, epochs=20, batch_size=16):
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

            # Категорія → мережа → продукт
            category_dir = os.path.join(base_dir, network, category_name.replace(' ', '_'))
            os.makedirs(category_dir, exist_ok=True)

            # Паралельна обробка
            pool = Pool(processes=cpu_count())  # або менше — напр. processes=4
            func = partial(predict_for_product, df=df, category_name=category_name,
                           category_dir=category_dir, look_back=look_back,
                           epochs=epochs, batch_size=batch_size)
            results = pool.map(func, products)
            pool.close()
            pool.join()

            for res in results:
                print("  ", res)

if __name__ == "__main__":
    batch_predict_all_categories()
