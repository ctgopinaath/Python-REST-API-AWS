# Django REST API - Products (External JSON)

A Django REST Framework API for managing products. Data is persisted in `products.json` — changes survive server restarts. Same functionality as `flask-json/`.

## Prerequisites

- Python 3.8+
- pip

## Install

```bash
pip install django djangorestframework
```

## Run

```bash
python manage.py runserver 8080
```

Server runs on: `http://127.0.0.1:8080`

## Endpoints

### GET all products
```bash
curl http://127.0.0.1:8080/products/
```

### GET products by category
```bash
curl http://127.0.0.1:8080/products/?category=Electronics
```

### GET product by ID
```bash
curl http://127.0.0.1:8080/products/1/
```

### POST create product
```bash
curl -X POST http://127.0.0.1:8080/products/create/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Mouse", "price": 29.99, "category": "Electronics", "stock": 75}'
```

### PUT update product
```bash
curl -X PUT http://127.0.0.1:8080/products/1/update/ \
  -H "Content-Type: application/json" \
  -d '{"price": 899.99, "stock": 40}'
```

### DELETE product
```bash
curl -X DELETE http://127.0.0.1:8080/products/1/delete/
```

## File Structure

```
Django/
├── manage.py         # Django entry point
├── settings.py       # Minimal Django settings
├── urls.py           # URL routes
├── views.py          # API logic (reads/writes products.json)
├── products.json     # Data file (persisted on disk)
└── djang-json.py     # Old reference file (users example)
```

## Note
Data is stored in `products.json`. POST, PUT, and DELETE all update the file on disk permanently — same behaviour as `flask-json/`.
