import json
import os
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

DATA_FILE = os.path.join(os.path.dirname(__file__), "products.json")


def load_products():
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_products(products):
    with open(DATA_FILE, "w") as f:
        json.dump(products, f, indent=4)


@api_view(["GET"])
def get_all_products(request):
    products = load_products()
    category = request.query_params.get("category")
    if category:
        products = [p for p in products if p["category"].lower() == category.lower()]
    return Response({"total": len(products), "products": products})


@api_view(["GET"])
def get_product(request, product_id):
    products = load_products()
    product = next((p for p in products if p["id"] == product_id), None)
    if not product:
        return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
    return Response(product)


@api_view(["POST"])
def create_product(request):
    products = load_products()
    data = request.data
    new_product = {
        "id": max(p["id"] for p in products) + 1,
        "name": data.get("name"),
        "price": data.get("price"),
        "category": data.get("category"),
        "stock": data.get("stock", 0),
    }
    products.append(new_product)
    save_products(products)
    return Response({"message": "Product created", "product": new_product}, status=status.HTTP_201_CREATED)


@api_view(["PUT"])
def update_product(request, product_id):
    products = load_products()
    product = next((p for p in products if p["id"] == product_id), None)
    if not product:
        return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
    data = request.data
    product.update({k: v for k, v in data.items() if k != "id"})
    save_products(products)
    return Response({"message": "Product updated", "product": product})


@api_view(["DELETE"])
def delete_product(request, product_id):
    products = load_products()
    product = next((p for p in products if p["id"] == product_id), None)
    if not product:
        return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
    updated = [p for p in products if p["id"] != product_id]
    save_products(updated)
    return Response({"message": f"Product {product_id} deleted"})
