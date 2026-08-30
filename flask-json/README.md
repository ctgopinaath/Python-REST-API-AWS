# Flask Products API (External JSON)

REST API for managing products. Data is persisted in `products.json` — changes survive server restarts.

## Install & Run

```bash
pip install flask
python3 app.py
```

Server runs on: `http://127.0.0.1:5001`

## Endpoints

### GET all products
```bash
curl http://127.0.0.1:5001/products
```

### GET products by category
```bash
curl http://127.0.0.1:5001/products?category=Electronics
```

### GET product by ID
```bash
curl http://127.0.0.1:5001/products/1
```

### POST create product
```bash
curl -X POST http://127.0.0.1:5001/products \
  -H "Content-Type: application/json" \
  -d '{"name": "Mouse", "price": 29.99, "category": "Electronics", "stock": 75}'
```

### PUT update product
```bash
curl -X PUT http://127.0.0.1:5001/products/1 \
  -H "Content-Type: application/json" \
  -d '{"price": 899.99, "stock": 40}'
```

### DELETE product
```bash
curl -X DELETE http://127.0.0.1:5001/products/1
```

## Note
Data is stored in `products.json`. POST, PUT, and DELETE all update the file on disk permanently.
