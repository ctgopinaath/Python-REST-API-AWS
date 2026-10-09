# FastAPI - Users API

A FastAPI REST API for managing users with automatic docs.

> 📚 **New to FastAPI?** Follow the hands-on course in [LEARN_FASTAPI.md](LEARN_FASTAPI.md): what FastAPI is, its components, FastAPI vs Django, 7 lessons with runnable examples in [`examples/`](examples/) (CRUD, auth, a SQLite library project, advanced features, testing) and curl commands for every endpoint.

## Prerequisites

- Python 3.8+
- pip

## Install

```bash
pip install fastapi uvicorn
```

## Run

```bash
uvicorn app:app --reload
```

Server runs on: `http://127.0.0.1:8000`

## Interactive Docs

FastAPI auto-generates docs — open in browser:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Endpoints

### GET user by ID
```bash
curl http://127.0.0.1:8000/users/1
```

### POST create user
```bash
curl -X POST http://127.0.0.1:8000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Sam", "email": "sam@example.com"}'
```
