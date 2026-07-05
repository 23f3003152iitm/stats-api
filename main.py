import time
import uuid
from typing import List

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# --- CONFIGURATION ---
ALLOWED_ORIGIN = "https://dash-h5oeok.example.com"
YOUR_EMAIL = "23f3003152@gmail.com"  # <-- CHANGE THIS TO YOUR LOGIN EMAIL
# ---------------------

# We will NOT use FastAPI's built-in CORSMiddleware for the main logic,
# because we need origin-specific behavior: only one origin gets ACAO.
# Instead, we'll handle CORS manually in a custom middleware.

@app.middleware("http")
async def cors_and_timing_middleware(request: Request, call_next):
    # Generate unique ID for this request
    request_id = str(uuid.uuid4())

    # Start timing
    start = time.perf_counter()

    # Get origin header
    origin = request.headers.get("origin", "")

    # Call the actual route handler
    response: Response = await call_next(request)

    # Compute duration
    duration = time.perf_counter() - start

    # Set required headers on every response
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{duration:.6f}"

    # CORS logic: only add Access-Control-Allow-Origin for the allowed origin
    if origin == ALLOWED_ORIGIN:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        # Optional, but good practice for preflight:
        response.headers["Access-Control-Max-Age"] = "86400"

    return response


@app.get("/stats")
async def get_stats(values: str):
    """
    Expects: GET /stats?values=1,2,3,4
    Returns stats as JSON.
    """
    # Parse comma-separated integers
    try:
        raw_items = [v.strip() for v in values.split(",") if v.strip() != ""]
        if not raw_items:
            return {
                "error": "No values provided",
                "email": "23f3003152@gmail.com",
                "count": 0,
                "sum": 0,
                "min": 0,
                "max": 0,
                "mean": 0.0,
            }
        numbers: List[int] = [int(x) for x in raw_items]
    except ValueError:
        return {
            "error": "Invalid integer in values",
            "email": "23f3003152@gmail.com",
            "count": 0,
            "sum": 0,
            "min": 0,
            "max": 0,
            "mean": 0.0,
        }

    count = len(numbers)
    total = sum(numbers)
    minimum = min(numbers)
    maximum = max(numbers)
    mean = total / count if count > 0 else 0.0

    return {
        "email": "23f3003152@gmail.com",
        "count": count,
        "sum": total,
        "min": minimum,
        "max": maximum,
        "mean": round(mean, 6),  # enough precision to be within ±0.01
    }