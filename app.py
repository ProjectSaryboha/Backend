from flask import jsonify, Flask, request
from flask_cors import CORS
from analyzer.analyze import get_top_5_expensive_products, get_categories_sorted_by_average_price, \
    get_product_counts_by_category, get_products_by_price

app = Flask(__name__)
CORS(app)

@app.route("/top-products", methods=["GET"])
def top_products():
    market = request.args.get("market")
    model = request.args.get("model")
    return jsonify(get_top_5_expensive_products(market, model))

@app.route("/category-prices", methods=["GET"])
def category_prices():
    market = request.args.get("market")
    model = request.args.get("model")
    return jsonify(get_categories_sorted_by_average_price(market, model))

@app.route("/product-counts", methods=["GET"])
def product_counts():
    market = request.args.get("market")
    model = request.args.get("model")
    return jsonify(get_product_counts_by_category(market, model))

@app.route("/products-by-category", methods=["GET"])
def products_by_category():
    category = request.args.get("category")
    market = request.args.get("market")
    model = request.args.get("model")
    if not (category):
        return jsonify({"error": "Параметр category є обов'язковим"}), 400

    products = get_products_by_price(category, market, model)
    return jsonify(products)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)