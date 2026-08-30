import json
import boto3

BUCKET = "srm-test-my-products-bucket"
KEY = "products.json"

s3 = boto3.client("s3")


def load_products():
    obj = s3.get_object(Bucket=BUCKET, Key=KEY)
    return json.loads(obj["Body"].read())


def save_products(products):
    s3.put_object(Bucket=BUCKET, Key=KEY, Body=json.dumps(products, indent=4))


def lambda_handler(event, context):
    method = event["httpMethod"]
    path = event["path"]
    path_params = event.get("pathParameters") or {}
    query_params = event.get("queryStringParameters") or {}
    body = json.loads(event["body"]) if event.get("body") else {}

    products = load_products()

    # GET /products
    if method == "GET" and path == "/products":
        category = query_params.get("category")
        if category:
            products = [p for p in products if p["category"].lower() == category.lower()]
        return response(200, {"total": len(products), "products": products})

    # GET /products/{id}
    if method == "GET" and "id" in path_params:
        product = next((p for p in products if p["id"] == int(path_params["id"])), None)
        if not product:
            return response(404, {"error": "Product not found"})
        return response(200, product)

    # POST /products
    if method == "POST":
        new_product = {
            "id": max(p["id"] for p in products) + 1,
            "name": body.get("name"),
            "price": body.get("price"),
            "category": body.get("category"),
            "stock": body.get("stock", 0),
        }
        products.append(new_product)
        save_products(products)
        return response(201, {"message": "Product created", "product": new_product})

    # PUT /products/{id}
    if method == "PUT" and "id" in path_params:
        product = next((p for p in products if p["id"] == int(path_params["id"])), None)
        if not product:
            return response(404, {"error": "Product not found"})
        product.update({k: v for k, v in body.items() if k != "id"})
        save_products(products)
        return response(200, {"message": "Product updated", "product": product})

    # DELETE /products/{id}
    if method == "DELETE" and "id" in path_params:
        product = next((p for p in products if p["id"] == int(path_params["id"])), None)
        if not product:
            return response(404, {"error": "Product not found"})
        updated = [p for p in products if p["id"] != int(path_params["id"])]
        save_products(updated)
        return response(200, {"message": f"Product {path_params['id']} deleted"})

    return response(400, {"error": "Invalid request"})


def response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }
