"""
Lesson 02 - Pydantic models: request body validation, response_model, enums.

Run:  cd examples && uvicorn 02_models:app --reload
"""
from enum import Enum
from typing import List, Optional

from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

app = FastAPI(title="Lesson 02 - Models")


class Role(str, Enum):
    admin = "admin"
    editor = "editor"
    viewer = "viewer"


class Address(BaseModel):
    city: str
    pincode: str = Field(pattern=r"^\d{6}$")  # Indian 6-digit pincode


# What the client SENDS
class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    age: int = Field(ge=18, le=120)
    password: str = Field(min_length=8)
    role: Role = Role.viewer
    address: Optional[Address] = None  # nested model
    tags: List[str] = []


# What the server RETURNS (no password!)
class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: Role
    address: Optional[Address] = None
    tags: List[str] = []


_next_id = 1


@app.post("/users", response_model=UserOut, status_code=201)
def create_user(user: UserCreate):
    global _next_id
    data = user.model_dump()
    data["id"] = _next_id
    _next_id += 1
    # response_model filters out "password" even though it is in `data`
    return data


# Enum in the path: only admin/editor/viewer are accepted
@app.get("/roles/{role}")
def role_info(role: Role):
    can_edit = role in (Role.admin, Role.editor)
    return {"role": role, "can_edit": can_edit}


# Query validation with Query(...)
@app.get("/products")
def list_products(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    sort: str = Query("name", pattern="^(name|price)$"),
):
    return {"page": page, "size": size, "sort": sort}
