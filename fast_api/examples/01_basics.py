"""
Lesson 01 - Basics: path params, query params, type conversion.

Run:  cd examples && uvicorn 01_basics:app --reload
"""
from typing import Optional

from fastapi import FastAPI

app = FastAPI(title="Lesson 01 - Basics")


@app.get("/")
def root():
    return {"message": "Hello FastAPI"}


# Path parameter: /items/5  -> item_id is converted to int automatically.
# /items/abc returns a 422 validation error without any extra code.
@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}


# Query parameters: anything in the signature that is NOT in the path.
# /search?q=phone&limit=5
@app.get("/search")
def search(q: str, limit: int = 10, in_stock: Optional[bool] = None):
    return {"q": q, "limit": limit, "in_stock": in_stock}


# Path + query together: /users/7/orders?status=shipped
@app.get("/users/{user_id}/orders")
def user_orders(user_id: int, status: str = "all"):
    return {"user_id": user_id, "status": status}
