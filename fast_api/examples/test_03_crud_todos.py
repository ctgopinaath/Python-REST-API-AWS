"""
Lesson 07 - Testing with TestClient (no server needed).

Install: pip install pytest httpx
Run:     cd examples && pytest -v
"""
import importlib

from fastapi.testclient import TestClient

# File name starts with a digit, so import it with importlib
todos_module = importlib.import_module("03_crud_todos")
client = TestClient(todos_module.app)


def setup_function():
    # fresh "database" for each test
    todos_module.todos.clear()
    todos_module.next_id = 1


def test_create_and_get():
    r = client.post("/todos", json={"title": "Learn FastAPI", "priority": 3})
    assert r.status_code == 201
    todo_id = r.json()["id"]

    r = client.get(f"/todos/{todo_id}")
    assert r.status_code == 200
    assert r.json()["title"] == "Learn FastAPI"
    assert r.json()["done"] is False


def test_validation_error():
    r = client.post("/todos", json={"title": "", "priority": 9})
    assert r.status_code == 422


def test_patch_only_changes_sent_fields():
    client.post("/todos", json={"title": "Write tests", "priority": 2})
    r = client.patch("/todos/1", json={"done": True})
    assert r.json()["done"] is True
    assert r.json()["priority"] == 2


def test_filter_and_pagination():
    for i in range(5):
        client.post("/todos", json={"title": f"task {i}", "priority": i + 1})
    r = client.get("/todos", params={"min_priority": 3, "limit": 2})
    body = r.json()
    assert body["total"] == 3
    assert len(body["items"]) == 2


def test_delete_then_404():
    client.post("/todos", json={"title": "temp"})
    assert client.delete("/todos/1").status_code == 204
    assert client.get("/todos/1").status_code == 404
