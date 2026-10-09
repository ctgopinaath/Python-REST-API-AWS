"""
Lesson 04 - Dependency Injection + Authentication.

Shows:
  * Depends() for reusable logic (pagination, current user)
  * Bearer-token login flow (POST /login -> token -> Authorization header)
  * API-key header auth
  * Role-based access (admin-only route)

NOTE: Tokens here are simple random strings kept in memory to keep the lesson
dependency-free. In production use JWT (python-jose / PyJWT) and hash
passwords with passlib/bcrypt.

Run:  cd examples && uvicorn 04_auth_dependencies:app --reload
"""
import hashlib
import secrets
from typing import Dict

from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

app = FastAPI(title="Lesson 04 - Auth & Dependencies")


def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


# username -> user record
USERS: Dict[str, dict] = {
    "alice": {"username": "alice", "password": hash_pw("alice123"), "role": "admin"},
    "bob": {"username": "bob", "password": hash_pw("bob123"), "role": "viewer"},
}
TOKENS: Dict[str, str] = {}  # token -> username
API_KEYS = {"demo-key-123"}


class LoginIn(BaseModel):
    username: str
    password: str


# ---------- Dependencies ----------

def pagination(skip: int = 0, limit: int = 10) -> dict:
    """A reusable dependency: any route can ask for it."""
    return {"skip": skip, "limit": min(limit, 100)}


bearer = HTTPBearer(auto_error=False)


def get_current_user(creds: HTTPAuthorizationCredentials = Depends(bearer)) -> dict:
    if creds is None or creds.credentials not in TOKENS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return USERS[TOKENS[creds.credentials]]


def require_admin(user: dict = Depends(get_current_user)) -> dict:
    # Dependencies can depend on other dependencies (a chain)
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    return user


def verify_api_key(x_api_key: str = Header(...)) -> str:
    # Header "X-API-Key" maps to parameter x_api_key automatically
    if x_api_key not in API_KEYS:
        raise HTTPException(status_code=401, detail="Bad API key")
    return x_api_key


# ---------- Routes ----------

@app.post("/login")
def login(body: LoginIn):
    user = USERS.get(body.username)
    if not user or user["password"] != hash_pw(body.password):
        raise HTTPException(status_code=401, detail="Wrong username or password")
    token = secrets.token_hex(16)
    TOKENS[token] = user["username"]
    return {"access_token": token, "token_type": "bearer"}


@app.get("/me")
def me(user: dict = Depends(get_current_user)):
    return {"username": user["username"], "role": user["role"]}


@app.get("/admin/users")
def admin_list_users(admin: dict = Depends(require_admin), page: dict = Depends(pagination)):
    names = list(USERS)[page["skip"]: page["skip"] + page["limit"]]
    return {"requested_by": admin["username"], "users": names}


@app.post("/logout")
def logout(creds: HTTPAuthorizationCredentials = Depends(bearer), user: dict = Depends(get_current_user)):
    TOKENS.pop(creds.credentials, None)
    return {"message": f"Bye {user['username']}"}


# Machine-to-machine style auth with an API key header
@app.get("/reports/daily", dependencies=[Depends(verify_api_key)])
def daily_report():
    return {"orders": 42, "revenue": 125000}
