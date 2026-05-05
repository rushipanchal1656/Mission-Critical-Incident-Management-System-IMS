from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from sqlalchemy.exc import OperationalError
from prometheus_client import Counter, generate_latest
import time

from app.db import engine
from app.models import Base
from app.queue import enqueue

app = FastAPI()

# =========================
# Prometheus Metrics
# =========================
try:
    REQUEST_COUNT = Counter("api_requests_total", "Total API Requests")
except ValueError:
    REQUEST_COUNT = Counter._metrics.get("api_requests_total")

@app.middleware("http")
async def count_requests(request, call_next):
    REQUEST_COUNT.inc()
    response = await call_next(request)
    return response


# =========================
# Startup Logic (DB Init)
# =========================
MAX_RETRIES = 30

@app.on_event("startup")
def startup():
    for i in range(MAX_RETRIES):
        try:
            print("⏳ API waiting for DB...")
            Base.metadata.create_all(bind=engine)
            print("✅ DB Connected & Tables Created")
            return
        except OperationalError as e:
            print(f"❌ DB not ready: {e}")
            time.sleep(2)

    raise RuntimeError("Database not reachable after retries")


# =========================
# Health Endpoint
# =========================
@app.get("/health")
def health():
    return {"status": "ok"}


# =========================
# Metrics Endpoint
# =========================
@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")


# =========================
# Signal Ingestion Endpoint
# =========================
@app.post("/signal")
def send_signal(component_id: str):
    if not component_id:
        raise HTTPException(status_code=400, detail="component_id is required")

    payload = {
        "component_id": component_id,
        "timestamp": time.time()
    }

    try:
        enqueue(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SQS enqueue failed: {e}")

    return {"status": "queued", "component_id": component_id}