# Python API Examples

Comparison of REST API implementations using Flask, Flask with JSON file, FastAPI, and Django REST Framework.

## Prerequisites

- Python 3.8+
- pip

## Folder Structure

```
python_api/
├── flask/          # Flask - in-memory users API       (port 5000)
├── flask-json/     # Flask - file-based products API   (port 5001)
├── fast_api/       # FastAPI - users API                (port 8000)
├── Django/         # Django REST Framework - users API  (port 8000)
├── aws-lambda/     # Lambda + API Gateway + S3 - products API
└── e-commerce/     # FastAPI on Lambda + API Gateway + EventBridge + SNS + SQS
```

## Quick Install (all frameworks)

```bash
pip install flask fastapi uvicorn django djangorestframework
```

## Run Each App

| Folder | Command | Port |
|--------|---------|------|
| `flask/` | `python3 app.py` | 5000 |
| `flask-json/` | `python3 app.py` | 5001 |
| `fast_api/` | `uvicorn app:app --reload` | 8000 |
| `Django/` | `python manage.py runserver` | 8000 |

## Comparison

| Feature | Flask | Flask-JSON | FastAPI | Django RF |
|---------|-------|------------|---------|-----------|
| Auto Docs | No | No | Yes | No |
| Data Persistence | No (memory) | Yes (JSON file) | No (memory) | DB (ORM) |
| Speed | Fast | Fast | Fastest | Moderate |
| Setup Complexity | Simple | Simple | Simple | Complex |

See each folder's `README.md` for detailed commands.
