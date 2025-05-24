from flask import jsonify, Flask, request

from analyzer.analyze import get_top_5_expensive_products, get_categories_sorted_by_average_price, \
    get_product_counts_by_category, get_products_by_price
from analyzer.run_LSTM import batch_predict_all_categories
from analyzer.utils import import_json

app = Flask(__name__)
@app.route('/predict', methods=['POST'])
def predict():
    batch_predict_all_categories()
    import_json()
    return jsonify({"message": "Прогнозування завершено успішно."}), 200

@app.route("/top-products", methods=["GET"])
def top_products():
    return jsonify(get_top_5_expensive_products())

@app.route("/category-prices", methods=["GET"])
def category_prices():
    return jsonify(get_categories_sorted_by_average_price())

@app.route("/product-counts", methods=["GET"])
def product_counts():
    return jsonify(get_product_counts_by_category())

@app.route("/products-by-category", methods=["GET"])
def products_by_category():
    category = request.args.get("category")
    if not category:
        return jsonify({"error": "Параметр 'category' є обов'язковим"}), 400

    products = get_products_by_price(category)
    return jsonify(products)

if __name__ == "__main__":
    app.run(debug=True)