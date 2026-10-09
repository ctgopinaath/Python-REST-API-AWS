"""
Lesson 03 - Full CRUD: GET / POST / PUT / PATCH / DELETE, HTTPException,
filtering, pagination, status codes.

Run:  cd examples && uvicorn 03_crud_todos:app --reload
"""
from datetime import datetime, timezone
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query, Response, status
from pydantic import BaseModel, Field

app = FastAPI(title="Lesson 03 - Todo CRUD")


class TodoCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: str = ""
    priority: int = Field(1, ge=1, le=5)


class TodoUpdate(BaseModel):
    # All optional -> used by PATCH (partial update)
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    priority: Optional[int] = Field(None, ge=1, le=5)
    done: Optional[bool] = None


class Todo(TodoCreate):
    id: int
    done: bool = False
    created_at: datetime


class TodoPage(BaseModel):
    total: int
    skip: int
    limit: int
    items: List[Todo]


# "Database"
todos: Dict[int, Todo] = {}
next_id = 1


def get_or_404(todo_id: int) -> Todo:
    if todo_id not in todos:
        raise HTTPException(status_code=404, detail=f"Todo {todo_id} not found")
    return todos[todo_id]


@app.get("/todos", response_model=TodoPage)
def list_todos(
    done: Optional[bool] = None,
    min_priority: int = Query(1, ge=1, le=5),
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
):
    items = list(todos.values())
    if done is not None:
        items = [t for t in items if t.done == done]
    items = [t for t in items if t.priority >= min_priority]
    if search:
        items = [t for t in items if search.lower() in t.title.lower()]
    return {"total": len(items), "skip": skip, "limit": limit, "items": items[skip: skip + limit]}


@app.get("/todos/{todo_id}", response_model=Todo)
def get_todo(todo_id: int):
    return get_or_404(todo_id)


@app.post("/todos", response_model=Todo, status_code=status.HTTP_201_CREATED)
def create_todo(payload: TodoCreate):
    global next_id
    todo = Todo(id=next_id, created_at=datetime.now(timezone.utc), **payload.model_dump())
    todos[next_id] = todo
    next_id += 1
    return todo


# PUT = replace the whole resource
@app.put("/todos/{todo_id}", response_model=Todo)
def replace_todo(todo_id: int, payload: TodoCreate):
    old = get_or_404(todo_id)
    todos[todo_id] = Todo(id=todo_id, created_at=old.created_at, **payload.model_dump())
    return todos[todo_id]


# PATCH = change only the fields sent
@app.patch("/todos/{todo_id}", response_model=Todo)
def update_todo(todo_id: int, payload: TodoUpdate):
    old = get_or_404(todo_id)
    changes = payload.model_dump(exclude_unset=True)
    todos[todo_id] = old.model_copy(update=changes)
    return todos[todo_id]


@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int):
    get_or_404(todo_id)
    del todos[todo_id]
    return Response(status_code=status.HTTP_204_NO_CONTENT)
