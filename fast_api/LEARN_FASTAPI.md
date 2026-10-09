# Learn FastAPI: A Hands-On Course

This guide takes you from "Hello World" to a small multi-file project with a database, authentication, background tasks and tests. Every lesson is a runnable file in [`examples/`](examples/), and every endpoint comes with a `curl` command to try it.

---

## Table of Contents

1. [What is FastAPI?](#1-what-is-fastapi)
2. [FastAPI's components](#2-fastapis-components)
3. [FastAPI vs Django (and Flask)](#3-fastapi-vs-django-and-flask)
4. [Setup](#4-setup)
5. [curl crash course](#5-curl-crash-course)
6. [Course roadmap](#6-course-roadmap)
7. [Lesson 01: Basics (path and query params)](#lesson-01--basics)
8. [Lesson 02: Pydantic models and validation](#lesson-02--pydantic-models--validation)
9. [Lesson 03: Full CRUD (Todo API)](#lesson-03--full-crud-todo-api)
10. [Lesson 04: Dependency injection and auth](#lesson-04--dependency-injection--authentication)
11. [Lesson 05: Mini project (Library Management API)](#lesson-05--mini-project-library-management-api)
12. [Lesson 06: Advanced features](#lesson-06--advanced-features)
13. [Lesson 07: Testing](#lesson-07--testing)
14. [Practice exercises](#practice-exercises)
15. [Common errors and fixes](#common-errors--fixes)
16. [Where to go next](#where-to-go-next)

---

## 1. What is FastAPI?

**FastAPI** is a modern Python web framework for building **APIs**. It's built on two libraries:

| Library | Role |
|---------|------|
| **Starlette** | The web part: routing, requests, responses, middleware, WebSockets |
| **Pydantic** | The data part: validation, parsing and serialization using Python type hints |

You write ordinary Python functions with **type hints**, and FastAPI gives you these for free:

- ✅ **Validation**: wrong types or missing fields produce a clean `422` error automatically
- ✅ **Conversion**: `"5"` in a URL becomes the `int` `5`
- ✅ **Interactive docs**: Swagger UI at `/docs` and ReDoc at `/redoc`
- ✅ **Editor support**: autocomplete and type checking everywhere
- ✅ **Async support**: `async def` endpoints can handle many concurrent I/O calls
- ✅ **Speed**: among the fastest Python frameworks (on par with Node.js and Go for I/O-bound work)

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/hello/{name}")
def hello(name: str, times: int = 1):
    return {"message": f"Hello {name}! " * times}
```

```bash
uvicorn app:app --reload
curl "http://127.0.0.1:8000/hello/Gopi?times=2"
# {"message":"Hello Gopi! Hello Gopi! "}
```

### How a request flows

```
 curl / browser / frontend
          │  HTTP request
          ▼
   ┌──────────────┐
   │   Uvicorn    │  ASGI server: listens on port 8000
   └──────┬───────┘
          ▼
   ┌──────────────┐
   │  Middleware  │  CORS, timing, logging, auth headers...
   └──────┬───────┘
          ▼
   ┌──────────────┐
   │   Routing    │  match method + path  →  your function
   └──────┬───────┘
          ▼
   ┌──────────────┐
   │ Dependencies │  Depends(): DB session, current user, pagination...
   └──────┬───────┘
          ▼
   ┌──────────────┐
   │  Validation  │  Pydantic checks path/query/body  → 422 if bad
   └──────┬───────┘
          ▼
   ┌──────────────┐
   │ Your function│  business logic
   └──────┬───────┘
          ▼
   response_model filters/serializes  →  JSON response
```

---

## 2. FastAPI's Components

| Component | What it does | Example | Lesson |
|-----------|--------------|---------|--------|
| `FastAPI()` | The application object | `app = FastAPI(title="My API")` | 01 |
| **Path operations** | Decorators that map HTTP method + URL to a function | `@app.get`, `@app.post`, `@app.put`, `@app.patch`, `@app.delete` | 01, 03 |
| **Path parameters** | Variables inside the URL | `/users/{user_id}` → `user_id: int` | 01 |
| **Query parameters** | `?key=value` after the URL | `def f(q: str, limit: int = 10)` | 01 |
| **Request body** | JSON sent by the client, described by a Pydantic model | `def f(user: UserCreate)` | 02 |
| **Pydantic `BaseModel`** | Defines data shape and validation rules | `age: int = Field(ge=18)` | 02 |
| **`response_model`** | Controls what is returned (for example, hides passwords) | `@app.post(..., response_model=UserOut)` | 02 |
| **`Query`, `Path`, `Header`, `Body`, `File`** | Extra validation and metadata for each input type | `Query(10, ge=1, le=100)` | 02, 04, 06 |
| **`HTTPException`** | Returns an error status with a message | `raise HTTPException(404, "Not found")` | 03 |
| **Status codes** | `status.HTTP_201_CREATED` and others | `status_code=201` | 03 |
| **Dependency injection** | `Depends()`: reusable logic injected into routes | `user = Depends(get_current_user)` | 04 |
| **Security utilities** | `HTTPBearer`, `OAuth2PasswordBearer`, `APIKeyHeader` | `Depends(HTTPBearer())` | 04 |
| **`APIRouter`** | Splits a big app into modules | `router = APIRouter(prefix="/books")` | 05 |
| **Lifespan events** | Run code at startup and shutdown | `FastAPI(lifespan=lifespan)` | 05 |
| **Background tasks** | Run work after the response is sent | `background.add_task(send_email, ...)` | 05 |
| **Middleware** | Code that wraps every request | `@app.middleware("http")` | 06 |
| **CORS** | Lets browser frontends on other domains call the API | `CORSMiddleware` | 06 |
| **Exception handlers** | Custom error formats | `@app.exception_handler(MyError)` | 06 |
| **`UploadFile`** | File uploads | `file: UploadFile = File(...)` | 06 |
| **`StreamingResponse`** | Streams large or CSV data | `StreamingResponse(gen(), media_type="text/csv")` | 06 |
| **`async def`** | Non-blocking endpoints | `await asyncio.gather(...)` | 06 |
| **`TestClient`** | Tests the app without running a server | `client.get("/todos")` | 07 |
| **OpenAPI docs** | Auto-generated `/docs`, `/redoc`, `/openapi.json` | open in a browser | all |

---

## 3. FastAPI vs Django (and Flask)

### Quick verdict

- **FastAPI**: best for **APIs and microservices**, ML model serving, and high-concurrency I/O. You choose your own ORM, auth and so on.
- **Django** (+ Django REST Framework): best for **full web applications** with an admin panel, ORM, auth, templates and migrations, all built in ("batteries included").
- **Flask**: minimal and flexible. Good for small apps; you add everything yourself.

### Side-by-side comparison

| Feature | FastAPI | Django + DRF | Flask |
|---------|---------|--------------|-------|
| Type | API framework (micro) | Full-stack framework | Micro framework |
| First release | 2018 | 2005 | 2010 |
| Server interface | **ASGI** (async-native) | WSGI (ASGI partial) | WSGI |
| Async support | ✅ First-class | ⚠️ Partial (views yes, ORM limited) | ⚠️ Limited |
| Performance | ⚡ Very high | Moderate | Moderate |
| Data validation | ✅ Built in (Pydantic, type hints) | Serializers (more code) | ❌ Manual / extensions |
| Auto API docs | ✅ Swagger + ReDoc out of the box | ⚠️ Needs drf-spectacular | ❌ Needs extensions |
| ORM | ❌ Bring your own (SQLAlchemy, SQLModel, Tortoise) | ✅ Django ORM | ❌ Bring your own |
| Migrations | Alembic (separate) | ✅ Built in | Flask-Migrate |
| Admin panel | ❌ | ✅ Built in | ❌ |
| Auth / users | Tools only (`Depends` + security utils) | ✅ Full system | Flask-Login |
| Templates / HTML | Possible (Jinja2) but not the focus | ✅ Strong | ✅ Jinja2 |
| Learning curve | Easy (if you know type hints) | Steeper (many conventions) | Easiest |
| Project structure | You decide | Opinionated (apps, settings) | You decide |
| Best for | REST/ML APIs, microservices, real-time | CMS, e-commerce, admin-heavy apps | Small apps, prototypes |

### The same endpoint in each

**FastAPI** (validation and docs included):
```python
class User(BaseModel):
    name: str
    email: str

@app.post("/users", status_code=201)
def create_user(user: User):
    return user
```

**Django REST Framework** (needs a model, serializer, view and URL entry):
```python
# serializers.py
class UserSerializer(serializers.Serializer):
    name = serializers.CharField()
    email = serializers.EmailField()

# views.py
@api_view(["POST"])
def create_user(request):
    s = UserSerializer(data=request.data)
    s.is_valid(raise_exception=True)
    return Response(s.data, status=201)

# urls.py
urlpatterns = [path("users", create_user)]
```

**Flask** (no validation unless you write it):
```python
@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
    if "name" not in data or "email" not in data:
        return {"error": "missing fields"}, 400
    return data, 201
```

> Compare with the other folders in this repo: `../flask/`, `../flask-json/`, `../Django/`.

### When to pick which?

| Scenario | Pick |
|----------|------|
| Backend for a React or mobile app | **FastAPI** |
| Serving an ML model (`model.predict`) | **FastAPI** |
| Many concurrent calls to other APIs or DBs | **FastAPI** (async) |
| Internal admin dashboard with CRUD forms | **Django** |
| Content site or e-commerce with server-rendered HTML | **Django** |
| Tiny prototype or webhook | **Flask** or FastAPI |

---

## 4. Setup

```bash
cd fast_api
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Each lesson runs on port **8000** by default. Stop one (`Ctrl+C`) before starting the next, or use `--port 8001`.

Once a server is running, open **http://127.0.0.1:8000/docs**. You can try every endpoint from the browser.

---

## 5. curl Crash Course

| Flag | Meaning | Example |
|------|---------|---------|
| `-X METHOD` | HTTP method (GET is the default) | `-X POST`, `-X PUT`, `-X PATCH`, `-X DELETE` |
| `-H "K: V"` | Add a header | `-H "Content-Type: application/json"` |
| `-d '...'` | Request body (JSON) | `-d '{"name":"Sam"}'` |
| `-F "file=@path"` | Multipart form / file upload | `-F "file=@sales.csv"` |
| `-i` | Show response headers too | `curl -i URL` |
| `-s` | Silent (no progress bar) | `curl -s URL` |
| `-v` | Verbose: see the full request and response | debugging |
| `-o file` | Save output to a file | `-o out.csv` |
| `-w "%{http_code}"` | Print the status code | `-s -o /dev/null -w "%{http_code}\n"` |

**Pretty-print JSON:** append `| python3 -m json.tool` (or `| jq` if installed).

**Quote URLs that contain `?` or `&`:** `curl "http://127.0.0.1:8000/search?q=a&limit=5"`

**Windows CMD:** use double quotes and escape the inner ones:
`curl -X POST http://127.0.0.1:8000/todos -H "Content-Type: application/json" -d "{\"title\":\"x\"}"`

---

## 6. Course Roadmap

| # | File | Topics | Level |
|---|------|--------|-------|
| 00 | [`app.py`](app.py) | First GET and POST | ⭐ |
| 01 | [`examples/01_basics.py`](examples/01_basics.py) | Path and query params, type conversion | ⭐ |
| 02 | [`examples/02_models.py`](examples/02_models.py) | Pydantic, `Field` validation, nested models, enums, `response_model` | ⭐⭐ |
| 03 | [`examples/03_crud_todos.py`](examples/03_crud_todos.py) | Full CRUD, PUT vs PATCH, 404s, filters, pagination | ⭐⭐ |
| 04 | [`examples/04_auth_dependencies.py`](examples/04_auth_dependencies.py) | `Depends`, bearer token login, API keys, roles | ⭐⭐⭐ |
| 05 | [`examples/05_library_app/`](examples/05_library_app/) | Multi-file project, SQLite, routers, business rules, background tasks | ⭐⭐⭐⭐ |
| 06 | [`examples/06_advanced.py`](examples/06_advanced.py) | Middleware, CORS, custom errors, uploads, async, rate limiting, streaming | ⭐⭐⭐⭐ |
| 07 | [`examples/test_03_crud_todos.py`](examples/test_03_crud_todos.py) | Automated tests with `TestClient` | ⭐⭐⭐ |

Suggested pace: one lesson per day. Read the file, run it, run every curl command, then do the exercise at the end.

---

## Lesson 01: Basics

```bash
cd examples
uvicorn 01_basics:app --reload
```

```bash
# Root
curl http://127.0.0.1:8000/

# Path parameter (auto-converted to int)
curl http://127.0.0.1:8000/items/5
# {"item_id":5}

# Wrong type: automatic 422 error
curl http://127.0.0.1:8000/items/abc

# Query parameters (q required, limit and in_stock optional)
curl "http://127.0.0.1:8000/search?q=phone&limit=5&in_stock=true"
# {"q":"phone","limit":5,"in_stock":true}

# Missing required query param: 422
curl "http://127.0.0.1:8000/search"

# Path + query
curl "http://127.0.0.1:8000/users/7/orders?status=shipped"
```

**Key idea:** parameters in `{}` in the path are **path params**. Every other simple-typed parameter is a **query param**. A default value makes it optional.

---

## Lesson 02: Pydantic Models and Validation

```bash
uvicorn 02_models:app --reload
```

```bash
# Valid user (with nested address). Note: the password is NOT returned
curl -X POST http://127.0.0.1:8000/users \
  -H "Content-Type: application/json" \
  -d '{
        "name": "Ravi",
        "email": "ravi@example.com",
        "age": 25,
        "password": "secret123",
        "role": "editor",
        "address": {"city": "Chennai", "pincode": "600001"},
        "tags": ["python", "aws"]
      }'

# Invalid user: see detailed errors for every bad field
curl -X POST http://127.0.0.1:8000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "R", "email": "bad", "age": 10, "password": "x"}' | python3 -m json.tool

# Enum path param: only admin, editor or viewer allowed
curl http://127.0.0.1:8000/roles/admin
curl http://127.0.0.1:8000/roles/hacker      # 422

# Query validation with bounds and a regex
curl "http://127.0.0.1:8000/products?page=2&size=20&sort=price"
curl "http://127.0.0.1:8000/products?size=500"   # 422 (le=100)
```

**Key ideas:**
- Use **separate input and output models** (`UserCreate` vs `UserOut`) so secrets never leak.
- `Field(ge=, le=, min_length=, pattern=)` declares rules once, and FastAPI enforces them.

---

## Lesson 03: Full CRUD (Todo API)

```bash
uvicorn 03_crud_todos:app --reload
```

| Method | URL | Action | Success code |
|--------|-----|--------|--------------|
| GET | `/todos` | List (with filters and pagination) | 200 |
| GET | `/todos/{id}` | Get one | 200 / 404 |
| POST | `/todos` | Create | 201 |
| PUT | `/todos/{id}` | Replace the whole todo | 200 |
| PATCH | `/todos/{id}` | Update some fields | 200 |
| DELETE | `/todos/{id}` | Delete | 204 |

```bash
# CREATE
curl -X POST http://127.0.0.1:8000/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy milk", "priority": 2}'

curl -X POST http://127.0.0.1:8000/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Learn FastAPI", "description": "Finish lesson 3", "priority": 5}'

# READ all / one
curl http://127.0.0.1:8000/todos
curl http://127.0.0.1:8000/todos/1

# FILTER + SEARCH + PAGINATION
curl "http://127.0.0.1:8000/todos?done=false&min_priority=3"
curl "http://127.0.0.1:8000/todos?search=milk"
curl "http://127.0.0.1:8000/todos?skip=0&limit=1"

# PATCH: only change "done"
curl -X PATCH http://127.0.0.1:8000/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"done": true}'

# PUT: replace everything (fields not sent go back to their defaults)
curl -X PUT http://127.0.0.1:8000/todos/2 \
  -H "Content-Type: application/json" \
  -d '{"title": "Master FastAPI", "priority": 4}'

# DELETE (204 = no body). -i shows the status line
curl -i -X DELETE http://127.0.0.1:8000/todos/1

# 404 after delete
curl http://127.0.0.1:8000/todos/1
# {"detail":"Todo 1 not found"}
```

**Key ideas:**
- `PATCH` uses `model_dump(exclude_unset=True)` so only the fields the client sent are changed.
- A helper like `get_or_404()` avoids repeating "not found" checks.

---

## Lesson 04: Dependency Injection and Authentication

```bash
uvicorn 04_auth_dependencies:app --reload
```

Demo users: `alice / alice123` (admin), `bob / bob123` (viewer). Demo API key: `demo-key-123`.

```bash
# 1. Login and get a token
curl -X POST http://127.0.0.1:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "alice123"}'
# {"access_token":"3f2a...","token_type":"bearer"}

# 2. Save the token in a shell variable (Linux/Mac)
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"alice123"}' \
  | python3 -c 'import sys,json; print(json.load(sys.stdin)["access_token"])')
echo $TOKEN

# 3. Call protected routes with an Authorization header
curl http://127.0.0.1:8000/me -H "Authorization: Bearer $TOKEN"
curl "http://127.0.0.1:8000/admin/users?skip=0&limit=5" -H "Authorization: Bearer $TOKEN"

# No token: 401
curl http://127.0.0.1:8000/me

# Bob is not an admin: 403
BOB=$(curl -s -X POST http://127.0.0.1:8000/login -H "Content-Type: application/json" \
  -d '{"username":"bob","password":"bob123"}' | python3 -c 'import sys,json; print(json.load(sys.stdin)["access_token"])')
curl http://127.0.0.1:8000/admin/users -H "Authorization: Bearer $BOB"
# {"detail":"Admins only"}

# API key auth (machine-to-machine)
curl http://127.0.0.1:8000/reports/daily -H "X-API-Key: demo-key-123"
curl http://127.0.0.1:8000/reports/daily -H "X-API-Key: wrong"     # 401

# Logout (token stops working)
curl -X POST http://127.0.0.1:8000/logout -H "Authorization: Bearer $TOKEN"
```

**Dependency chain used here:**

```
admin_list_users
   ├── Depends(require_admin)
   │       └── Depends(get_current_user)
   │               └── Depends(HTTPBearer)   ← reads "Authorization: Bearer ..."
   └── Depends(pagination)                   ← reads ?skip=&limit=
```

**401 vs 403:** `401 Unauthorized` means "who are you?" (missing or bad credentials). `403 Forbidden` means "I know who you are, but you're not allowed."

> **Production note:** use **JWT** (`pip install pyjwt`) and **bcrypt** password hashing (`pip install passlib[bcrypt]`) instead of the in-memory tokens and SHA-256 used here.

---

## Lesson 05: Mini Project (Library Management API)

This is a more realistic use case: a **multi-file project** with a **SQLite database** and **real business rules**.

```
05_library_app/
├── main.py          # create app, lifespan (create tables), include routers
├── database.py      # SQLite connection as a `yield` dependency (commit/rollback/close)
├── schemas.py       # Pydantic models
└── routers/
    ├── books.py     # /books   (CRUD + availability computed in SQL)
    ├── members.py   # /members
    └── loans.py     # /loans   (borrow / return / overdue / fines)
```

**Business rules in `routers/loans.py`:**
1. A book can be borrowed only if a copy is available.
2. A member can hold at most **3** books at a time.
3. A member with an **overdue** book can't borrow anything new.
4. Late returns cost **₹5 per day**.
5. A book with open loans can't be deleted.
6. ISBNs and emails must be unique (`409 Conflict`).
7. A receipt is "sent" in a **background task** (printed in the server log).

```bash
cd examples/05_library_app
uvicorn main:app --reload
```

```bash
# Add books
curl -X POST http://127.0.0.1:8000/books -H "Content-Type: application/json" \
  -d '{"title":"Clean Code","author":"Robert Martin","isbn":"9780132350884","total_copies":2}'

curl -X POST http://127.0.0.1:8000/books -H "Content-Type: application/json" \
  -d '{"title":"Fluent Python","author":"Luciano Ramalho","isbn":"9781492056355","total_copies":1}'

# Duplicate ISBN: 409
curl -X POST http://127.0.0.1:8000/books -H "Content-Type: application/json" \
  -d '{"title":"Clean Code","author":"Robert Martin","isbn":"9780132350884"}'

# Add members
curl -X POST http://127.0.0.1:8000/members -H "Content-Type: application/json" \
  -d '{"name":"Priya","email":"priya@example.com"}'
curl -X POST http://127.0.0.1:8000/members -H "Content-Type: application/json" \
  -d '{"name":"Arun","email":"arun@example.com"}'

# Priya borrows "Fluent Python" (only 1 copy) for 7 days
curl -X POST http://127.0.0.1:8000/loans/borrow -H "Content-Type: application/json" \
  -d '{"book_id":2,"member_id":1,"days":7}'

# Arun tries the same book: 409 "No copies available"
curl -X POST http://127.0.0.1:8000/loans/borrow -H "Content-Type: application/json" \
  -d '{"book_id":2,"member_id":2}'

# Search and filter books
curl "http://127.0.0.1:8000/books?available=true"
curl "http://127.0.0.1:8000/books?author=martin"

# Can't delete a borrowed book: 409
curl -X DELETE http://127.0.0.1:8000/books/2

# Loans of a member / active loans / overdue list
curl "http://127.0.0.1:8000/loans?member_id=1"
curl "http://127.0.0.1:8000/loans?active_only=true"
curl http://127.0.0.1:8000/loans/overdue

# Return the book (fine is calculated automatically)
curl -X POST http://127.0.0.1:8000/loans/1/return

# Return again: 409 "Already returned"
curl -X POST http://127.0.0.1:8000/loans/1/return
```

**Try the overdue rule:** Arun borrows a book, you backdate the due date in the DB, and then Arun is blocked:

```bash
# Arun borrows "Clean Code"
curl -X POST http://127.0.0.1:8000/loans/borrow -H "Content-Type: application/json" \
  -d '{"book_id":1,"member_id":2}'

# Make all open loans overdue (no sqlite3 CLI needed)
python3 -c "import sqlite3; c=sqlite3.connect('library.db'); c.execute(\"UPDATE loans SET due_on='2026-01-01' WHERE returned_on IS NULL\"); c.commit()"

curl http://127.0.0.1:8000/loans/overdue              # shows the fine in rupees

# Arun tries to borrow again: 403 "Member has overdue books - return them first"
curl -X POST http://127.0.0.1:8000/loans/borrow -H "Content-Type: application/json" \
  -d '{"book_id":1,"member_id":2}'
```

Delete `library.db` to start fresh.

---

## Lesson 06: Advanced Features

```bash
cd examples
uvicorn 06_advanced:app --reload
```

```bash
# Middleware adds X-Request-ID and X-Process-Time-ms headers to every response
curl -i -X POST "http://127.0.0.1:8000/wallets/bob/pay?amount=50"

# Custom exception and handler: structured error JSON
curl -X POST "http://127.0.0.1:8000/wallets/bob/pay?amount=5000"
# {"error":"INSUFFICIENT_BALANCE","needed":5000,"available":50,"path":"/wallets/bob/pay"}

# Rate limiting: the 6th call within 10 seconds gets 429
for i in 1 2 3 4 5 6; do curl -s -o /dev/null -w "%{http_code} " http://127.0.0.1:8000/limited; done; echo
# 200 200 200 200 200 429

# File upload (multipart)
printf 'product,qty,price\nPen,10,5.5\nBook,2,250\nPen,4,5.5\n' > sales.csv
curl -X POST http://127.0.0.1:8000/upload/sales-csv -F "file=@sales.csv"
# {"filename":"sales.csv","rows":3,"revenue_by_product":{"Pen":77.0,"Book":500.0},"grand_total":577.0}

# Async concurrency: 3 calls (1s + 0.5s + 0.8s) finish in about 1s total
curl http://127.0.0.1:8000/dashboard

# Streaming CSV download
curl "http://127.0.0.1:8000/export/numbers?n=5"
curl -o numbers.csv "http://127.0.0.1:8000/export/numbers?n=1000"

# CORS preflight (what a browser sends before calling from localhost:3000)
curl -i -X OPTIONS http://127.0.0.1:8000/dashboard \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: GET"
```

### `def` vs `async def`: which one?

| Use | When |
|-----|------|
| `async def` | You `await` async libraries (httpx, asyncpg, motor, `asyncio.sleep`) |
| plain `def` | You call blocking code (sqlite3, requests, pandas). FastAPI runs it in a thread pool, so it won't block the server |
| ❌ Never | Call blocking code (`time.sleep`, `requests.get`) inside `async def`, because it freezes the whole server |

---

## Lesson 07: Testing

```bash
cd examples
pytest -v
```

`TestClient` calls your app in-process, so there's no server and no curl:

```python
from fastapi.testclient import TestClient
client = TestClient(app)

def test_create():
    r = client.post("/todos", json={"title": "Learn FastAPI"})
    assert r.status_code == 201
```

See [`examples/test_03_crud_todos.py`](examples/test_03_crud_todos.py) for 5 complete tests: create, validation, patch, filters and delete.

---

## Practice Exercises

| # | Exercise | Builds on |
|---|----------|-----------|
| 1 | Add `GET /items/{item_id}/price?currency=INR` to lesson 01 that converts a fixed price to USD or EUR | 01 |
| 2 | Add a `phone` field to `UserCreate` with a 10-digit regex, and return it in `UserOut` | 02 |
| 3 | Add `due_date` to todos and a `GET /todos/overdue` endpoint | 03 |
| 4 | Add `sort_by=priority\|created_at` and `order=asc\|desc` to `GET /todos` | 03 |
| 5 | Add `POST /register` to lesson 04 that creates a new viewer user (409 if the username exists) | 04 |
| 6 | Make tokens expire after 30 minutes | 04 |
| 7 | Library: add `PATCH /books/{id}` to change `total_copies` (reject a value below the number currently borrowed) | 05 |
| 8 | Library: add `GET /members/{id}/summary` returning active loans, total fines and history count | 05 |
| 9 | Library: protect `POST /books` and `DELETE /books` with the admin dependency from lesson 04 | 04 + 05 |
| 10 | Write pytest tests for the library's borrow rules (no copies, limit of 3, overdue) | 05 + 07 |
| 11 | Replace sqlite3 with **SQLAlchemy** or **SQLModel**, and add **Alembic** migrations | 05 |
| 12 | Containerize lesson 05 with a `Dockerfile` and deploy it (see `../aws-lambda/` and use **Mangum** for Lambda) | 05 |

---

## Common Errors and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `422 Unprocessable Entity` | Wrong type or missing field | Read the `detail` list: `loc` tells you which field |
| `{"detail":"Not Found"}` | Wrong URL or method | Check `/docs`, trailing slashes and GET vs POST |
| `405 Method Not Allowed` | Path exists, but not for that method | Use the right `-X` |
| Body ignored or 422 on POST | Missing `Content-Type: application/json` | Add `-H "Content-Type: application/json"` |
| `Form data requires "python-multipart"` | Upload library missing | `pip install python-multipart` |
| `Error loading ASGI app. Could not import module` | Running uvicorn from the wrong folder | `cd` into the folder that contains the file |
| `Address already in use` | Port 8000 is busy | Stop the other server, or use `--port 8001` |
| Server freezes under load | Blocking call inside `async def` | Use plain `def` or an async library |

---

## Where to Go Next

- 📘 Official tutorial: https://fastapi.tiangolo.com/tutorial/
- 🗄️ SQL databases with SQLModel: https://sqlmodel.tiangolo.com/
- 🔐 OAuth2 + JWT: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
- 🧱 Bigger apps: https://fastapi.tiangolo.com/tutorial/bigger-applications/
- 🚀 Deployment (Docker, Gunicorn, AWS Lambda with Mangum): https://fastapi.tiangolo.com/deployment/
