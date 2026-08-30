# Flask Users API

In-memory REST API for managing users. Data resets on server restart.

## Install & Run

```bash
pip install flask
python3 app.py
```

Server runs on: `http://127.0.0.1:5000`

## Endpoints

### GET all users
```bash
curl http://127.0.0.1:5000/users
```

### GET user by ID
```bash
curl http://127.0.0.1:5000/users/1
```

### POST create user
```bash
curl -X POST http://127.0.0.1:5000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Sam", "email": "sam@example.com", "age": 25, "role": "user"}'
```

### PUT update user
```bash
curl -X PUT http://127.0.0.1:5000/users/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "John Updated", "age": 30}'
```

### DELETE user
```bash
curl -X DELETE http://127.0.0.1:5000/users/1
```

## Note
Data is stored in-memory — all changes are lost when the server restarts.
