from fastapi import FastAPI

app = FastAPI()


@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {
        "id": user_id,
        "name": "John",
        "email": "john@example.com"
    }


@app.post("/users", status_code=201)
def create_user(user: dict):
    return {
        "message": "User created",
        "user": user
    }
