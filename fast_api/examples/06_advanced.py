"""
Lesson 06 - Advanced features:
  * Middleware (request timing + request id header)
  * CORS (allow a React/Angular frontend to call the API)
  * Custom exception + global exception handler
  * File upload (CSV) and processing  -> needs: pip install python-multipart
  * async endpoints running work concurrently (asyncio.gather)
  * Simple in-memory rate limiter as a dependency
  * Streaming response

Run:  cd examples && uvicorn 06_advanced:app --reload
"""
import asyncio
import csv
import io
import time
import uuid
from collections import defaultdict, deque

from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse

app = FastAPI(title="Lesson 06 - Advanced")

# ---------- CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # your frontend URL
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Custom middleware ----------
@app.middleware("http")
async def add_timing_and_request_id(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Request-ID"] = str(uuid.uuid4())
    response.headers["X-Process-Time-ms"] = f"{(time.perf_counter() - start) * 1000:.2f}"
    return response


# ---------- Custom exception + handler ----------
class InsufficientBalance(Exception):
    def __init__(self, needed: int, available: int):
        self.needed = needed
        self.available = available


@app.exception_handler(InsufficientBalance)
async def insufficient_balance_handler(request: Request, exc: InsufficientBalance):
    return JSONResponse(
        status_code=400,
        content={
            "error": "INSUFFICIENT_BALANCE",
            "needed": exc.needed,
            "available": exc.available,
            "path": request.url.path,
        },
    )


WALLETS = {"alice": 500, "bob": 100}


@app.post("/wallets/{name}/pay")
def pay(name: str, amount: int):
    if name not in WALLETS:
        raise HTTPException(404, "Wallet not found")
    if WALLETS[name] < amount:
        raise InsufficientBalance(needed=amount, available=WALLETS[name])
    WALLETS[name] -= amount
    return {"name": name, "balance": WALLETS[name]}


# ---------- Rate limiting dependency ----------
HITS = defaultdict(deque)  # client ip -> timestamps


def rate_limit(request: Request, max_calls: int = 5, per_seconds: int = 10):
    ip = request.client.host if request.client else "unknown"
    now = time.time()
    q = HITS[ip]
    while q and q[0] < now - per_seconds:
        q.popleft()
    if len(q) >= max_calls:
        raise HTTPException(429, f"Too many requests: max {max_calls} per {per_seconds}s")
    q.append(now)


@app.get("/limited", dependencies=[Depends(rate_limit)])
def limited():
    return {"message": "You are within the rate limit"}


# ---------- File upload ----------
@app.post("/upload/sales-csv")
async def upload_sales(file: UploadFile = File(...)):
    """Upload a CSV with columns: product,qty,price  -> get totals per product."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(400, "Please upload a .csv file")
    text = (await file.read()).decode("utf-8")
    totals = defaultdict(float)
    rows = 0
    for row in csv.DictReader(io.StringIO(text)):
        try:
            totals[row["product"]] += int(row["qty"]) * float(row["price"])
        except (KeyError, ValueError):
            raise HTTPException(422, f"Bad row {rows + 1}: {row}")
        rows += 1
    return {
        "filename": file.filename,
        "rows": rows,
        "revenue_by_product": dict(totals),
        "grand_total": sum(totals.values()),
    }


# ---------- async concurrency ----------
async def fake_service(name: str, delay: float) -> dict:
    await asyncio.sleep(delay)  # pretend this is an HTTP call / DB query
    return {"service": name, "took_s": delay}


@app.get("/dashboard")
async def dashboard():
    """Calls 3 'services' in parallel: total time ~1s, not 1+0.5+0.8s."""
    start = time.perf_counter()
    results = await asyncio.gather(
        fake_service("orders", 1.0),
        fake_service("users", 0.5),
        fake_service("inventory", 0.8),
    )
    return {"results": results, "total_s": round(time.perf_counter() - start, 2)}


# ---------- Streaming ----------
@app.get("/export/numbers")
def export_numbers(n: int = 5):
    def gen():
        yield "id,square\n"
        for i in range(1, n + 1):
            yield f"{i},{i * i}\n"

    return StreamingResponse(
        gen(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=numbers.csv"},
    )
