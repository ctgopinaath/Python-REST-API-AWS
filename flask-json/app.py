import json
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

DATA_FILE = os.path.join(os.path.dirname(__file__), "products.json")


def load_products():
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_products(products):
    with open(DATA_FILE, "w") as f:
        json.dump(products, f, indent=4)


@app.route("/products", methods=["GET"])
def get_all_products():
    products = load_products()
    category = request.args.get("category")
    if category:
        products = [p for p in products if p["category"].lower() == category.lower()]
    return jsonify({"total": len(products), "products": products})


@app.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    products = load_products()
    product = next((p for p in products if p["id"] == product_id), None)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(product)


@app.route("/products", methods=["POST"])
def create_product():
    products = load_products()
    data = request.get_json()
    new_product = {
        "id": max(p["id"] for p in products) + 1,
        "name": data.get("name"),
        "price": data.get("price"),
        "category": data.get("category"),
        "stock": data.get("stock", 0),
    }
    products.append(new_product)
    save_products(products)
    return jsonify({"message": "Product created", "product": new_product}), 201


@app.route("/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    products = load_products()
    product = next((p for p in products if p["id"] == product_id), None)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    data = request.get_json()
    product.update({k: v for k, v in data.items() if k != "id"})
    save_products(products)
    return jsonify({"message": "Product updated", "product": product})


@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    products = load_products()
    product = next((p for p in products if p["id"] == product_id), None)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    updated = [p for p in products if p["id"] != product_id]
    save_products(updated)
    return jsonify({"message": f"Product {product_id} deleted"})


if __name__ == "__main__":
    app.run(debug=True, port=5001)
