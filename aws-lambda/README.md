# Products API — AWS Lambda + API Gateway

Same products API as `flask-json/` but serverless on AWS. No server to manage — AWS runs your code on demand.

---

## How It Works

```
Browser / curl
     |
     v
API Gateway  (handles HTTP routes)
     |
     v
Lambda Function  (your Python code runs here)
     |
     v
S3 Bucket  (stores products.json — replaces local file)
```

> Lambda is stateless — it cannot write to local disk. So products.json must live in an S3 bucket.

---

## Prerequisites

- AWS account
- AWS CLI installed and configured (`aws configure`)
- Python 3.x

---

## Step 1 — Create an S3 Bucket (to store products.json)

```bash
aws s3 mb s3://my-products-bucket
```

Upload the initial data:

```bash
aws s3 cp products.json s3://my-products-bucket/products.json
```

`products.json`:
```json
[
    {"id": 1, "name": "Laptop", "price": 999.99, "category": "Electronics", "stock": 50},
    {"id": 2, "name": "Headphones", "price": 149.99, "category": "Electronics", "stock": 120}
]
```

---

## Step 2 — Write the Lambda Function

Create `lambda_function.py`:

```python
import json
import boto3
import os

BUCKET = "my-products-bucket"
KEY = "products.json"

s3 = boto3.client("s3")


def load_products():
    obj = s3.get_object(Bucket=BUCKET, Key=KEY)
    return json.loads(obj["Body"].read())


def save_products(products):
    s3.put_object(Bucket=BUCKET, Key=KEY, Body=json.dumps(products, indent=4))


def lambda_handler(event, context):
    # HTTP API (v2) uses requestContext.http.method
    # REST API (v1) uses httpMethod — handle both
    if "httpMethod" in event:
        method = event["httpMethod"]
        path = event["path"]
    else:
        method = event["requestContext"]["http"]["method"]
        path = event["rawPath"]

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
```

---

## Step 3 — Package and Deploy Lambda

```bash
# Zip the function
zip function.zip lambda_function.py

# Create Lambda function
aws lambda create-function \
  --function-name products-api \
  --runtime python3.13 \
  --role arn:aws:iam::YOUR_ACCOUNT_ID:role/lambda-role \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://function.zip
```

> Replace `YOUR_ACCOUNT_ID` with your actual AWS account ID.

---

## Step 4 — Give Lambda Access to S3

Attach this policy to your Lambda IAM role:

```json
{
  "Effect": "Allow",
  "Action": ["s3:GetObject", "s3:PutObject"],
  "Resource": "arn:aws:s3:::my-products-bucket/*"
}
```

---

## Step 5 — Create API Gateway

```bash
# Create REST API
aws apigateway create-rest-api --name "products-api"

# Note the 'id' from the output — that is your API_ID
```

Then in AWS Console (easier for wiring routes):

1. Go to **API Gateway → Create API → REST API**
2. Create resource `/products`
3. Add methods: `GET`, `POST`
4. Create resource `/products/{id}`
5. Add methods: `GET`, `PUT`, `DELETE`
6. For each method → Integration type → **Lambda Function** → select `products-api`
7. ⚠️ **Check "Use Lambda Proxy Integration"** — this is critical, without it the event will be empty `{}`
8. Click **Actions → Deploy API** → create stage `PROD`

> **CLI alternative** (avoids the proxy integration mistake):
> ```bash
> aws apigateway put-integration \
>   --rest-api-id YOUR_API_ID \
>   --resource-id YOUR_RESOURCE_ID \
>   --http-method GET \
>   --type AWS_PROXY \
>   --integration-http-method POST \
>   --uri arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:REGION:ACCOUNT_ID:function:FUNCTION_NAME/invocations
> ```

---

## Step 6 — Test

After deploying, API Gateway gives you a base URL like:

```
https://abc123.execute-api.us-east-1.amazonaws.com/prod
```

```bash
# GET all products
curl https://abc123.execute-api.us-east-1.amazonaws.com/prod/products

# GET by category
curl https://abc123.execute-api.us-east-1.amazonaws.com/prod/products?category=Electronics

# GET by ID
curl https://abc123.execute-api.us-east-1.amazonaws.com/prod/products/1

# POST create
curl -X POST https://abc123.execute-api.us-east-1.amazonaws.com/prod/products \
  -H "Content-Type: application/json" \
  -d '{"name": "Mouse", "price": 29.99, "category": "Electronics", "stock": 75}'

# PUT update
curl -X PUT https://abc123.execute-api.us-east-1.amazonaws.com/prod/products/1 \
  -H "Content-Type: application/json" \
  -d '{"price": 899.99}'

# DELETE
curl -X DELETE https://abc123.execute-api.us-east-1.amazonaws.com/prod/products/1
```

---

## Troubleshooting

### `{"message": "Missing Authentication Token"}`
This is a **misleading AWS error** — it does NOT mean an auth/token problem. It actually means **API Gateway could not find the route** you are hitting. Common causes:

| Cause | Fix |
|-------|-----|
| Wrong URL path (e.g. hitting `/` instead of `/products/`) | Check the exact URL — include the stage name (`/prod/products/`) |
| API not deployed after adding routes | Go to API Gateway → **Deploy API** → select stage → Deploy |
| Method not configured (e.g. POST missing) | Add the missing HTTP method to the resource in API Gateway |
| Stage name missing in URL | URL must include stage: `.../prod/products/` not `.../products/` |
| Trailing slash mismatch | Try with and without trailing slash |

**Quick checklist:**
1. Is the stage name in the URL? → `https://abc123.execute-api.us-east-1.amazonaws.com/prod/products`
2. Did you click **Deploy API** after creating routes?
3. Does the route and method (GET/POST/PUT/DELETE) exist in API Gateway?
4. Is Lambda linked to every method, not just one?

---

## Comparison vs Flask-JSON

| Feature | flask-json | AWS Lambda + API Gateway |
|---------|------------|--------------------------|
| Runs on | Your machine | AWS Cloud |
| Data storage | Local `products.json` file | S3 bucket |
| Always on | Yes (while server runs) | No (runs only on request) |
| Cost | Free (local) | Pay per request |
| Scales automatically | No | Yes |
| Setup time | 1 minute | ~30 minutes |
