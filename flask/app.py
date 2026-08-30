from flask import Flask, request, jsonify

app = Flask(__name__)

# In-memory users list
users = [
    {"id": 1, "name": "John", "email": "john@example.com", "age": 28, "role": "admin"},
    {"id": 2, "name": "Alice", "email": "alice@example.com", "age": 24, "role": "user"},
    {"id": 3, "name": "Bob", "email": "bob@example.com", "age": 32, "role": "user"},
]


@app.route("/users", methods=["GET"])
def get_all_users():
    return jsonify({"total": len(users), "users": users})


@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = next((u for u in users if u["id"] == user_id), None)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user)


@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
    new_user = {
        "id": len(users) + 1,
        "name": data.get("name"),
        "email": data.get("email"),
        "age": data.get("age"),
        "role": data.get("role", "user"),
    }
    users.append(new_user)
    return jsonify({"message": "User created", "user": new_user}), 201


@app.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    user = next((u for u in users if u["id"] == user_id), None)
    if not user:
        return jsonify({"error": "User not found"}), 404
    data = request.get_json()
    user.update({k: v for k, v in data.items() if k != "id"})
    return jsonify({"message": "User updated", "user": user})


@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    global users
    user = next((u for u in users if u["id"] == user_id), None)
    if not user:
        return jsonify({"error": "User not found"}), 404
    users = [u for u in users if u["id"] != user_id]
    return jsonify({"message": f"User {user_id} deleted"})


if __name__ == "__main__":
    app.run(debug=True)
