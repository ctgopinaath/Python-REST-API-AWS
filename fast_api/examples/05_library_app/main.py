"""
Lesson 05 - Mini project: Library Management API.

Shows a real project layout:
  main.py          -> app creation, startup, router wiring
  database.py      -> SQLite connection as a `yield` dependency
  schemas.py       -> Pydantic request/response models
  routers/*.py     -> one APIRouter per resource (books, members, loans)

Run:  cd examples/05_library_app && uvicorn main:app --reload
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import init_db
from routers import books, loans, members


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()  # runs once at startup
    yield
    # anything here runs at shutdown


app = FastAPI(title="Library API", version="1.0.0", lifespan=lifespan)

app.include_router(books.router)
app.include_router(members.router)
app.include_router(loans.router)


@app.get("/health", tags=["ops"])
def health():
    return {"status": "ok"}
