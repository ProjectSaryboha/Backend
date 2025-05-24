import pandas as pd

def get_products_by_price(category, input_file="predicted_products.json"):
    try:
        df = pd.read_json(input_file, encoding="utf-8")
    except Exception as e:
        print(f"Помилка при читанні файлу: {e}")
        return []

    if 'category' not in df.columns or 'price_prediction' not in df.columns:
        print("У даних немає потрібних колонок 'category' або 'price_prediction'")
        return []

    df = df[pd.to_numeric(df['price_prediction'], errors='coerce').notnull()]
    df['price_prediction'] = df['price_prediction'].astype(float)

    filtered = df[df['category'] == category]

    if filtered.empty:
        print(f"Категорію '{category}' не знайдено.")
        return []

    sorted_products = filtered.sort_values(by='price_prediction', ascending=True)

    if 'name' in sorted_products.columns:
        sorted_products = sorted_products[['name', 'price_prediction']]
    else:
        print("У даних немає колонки 'name'")
        return []

    return sorted_products.to_dict(orient='records')

def get_top_5_expensive_products(input_file="predicted_products.json"):
    try:
        df = pd.read_json(input_file, encoding="utf-8")
    except Exception as e:
        print(f"Помилка при читанні файлу: {e}")
        return []

    if 'price_prediction' not in df.columns:
        print("У даних немає колонки 'price_prediction'")
        return []

    df = df[pd.to_numeric(df['price_prediction'], errors='coerce').notnull()]
    df['price_prediction'] = df['price_prediction'].astype(float)

    top_5 = df.sort_values(by='price_prediction', ascending=False).head(5)

    if 'name' in top_5.columns:
        top_5 = top_5[['name', 'price_prediction']]
    else:
        print("У даних немає колонки 'name'")
        return []

    result = top_5.to_dict(orient='records')
    return result

def get_categories_sorted_by_average_price(input_file="predicted_products.json"):
    try:
        df = pd.read_json(input_file, encoding="utf-8")
    except Exception as e:
        print(f"Помилка при читанні файлу: {e}")
        return []

    if 'price_prediction' not in df.columns or 'category' not in df.columns:
        print("У даних немає потрібних колонок 'price_prediction' або 'category'")
        return []

    df = df[pd.to_numeric(df['price_prediction'], errors='coerce').notnull()]
    df['price_prediction'] = df['price_prediction'].astype(float)

    grouped = df.groupby('category')['price_prediction'].max().reset_index()

    grouped = grouped.sort_values(by='price_prediction', ascending=False)


    result = grouped.to_dict(orient='records')
    return result

def get_product_counts_by_category(input_file="predicted_products.json"):
    try:
        df = pd.read_json(input_file, encoding="utf-8")
    except Exception as e:
        print(f"Помилка при читанні файлу: {e}")
        return []

    if 'category' not in df.columns:
        print("У даних немає колонки 'category'")
        return []

    category_counts = df['category'].value_counts().reset_index()
    category_counts.columns = ['category', 'count']

    result = category_counts.to_dict(orient='records')

    return result