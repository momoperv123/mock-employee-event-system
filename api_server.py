from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import json
import os

app = FastAPI()
Instrumentator().instrument(app).expose(app)

REQUEST_COUNTER = Counter("http_requests_total", "Total HTTP requests", ["method", "endpoint"])

@app.middleware("http")
async def count_requests(request, call_next):
    response = await call_next(request)
    REQUEST_COUNTER.labels(method=request.method, endpoint=request.url.path).inc()
    return response

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/payroll")
def get_payroll_data():
    path = "/data/payroll_state.json"
    if os.path.exists(path):
        with open(path, "r") as f: return json.load(f)
    return {"message": "No payroll data found"}

@app.get("/audit")
def get_payroll_data(limit: int = 10):
    path = "/data/audit_log.json"
    if os.path.exists(path):
        with open(path, "r") as f:
            lines = [json.loads(line) for line in f if line.strip()]
            return lines[-limit:] if len(lines) >= limit else lines
    return {"message": "No audit data found"}

@app.get("/dlq")
def get_dlq_events(limit: int = 10):
    path = "/data/dlq_log.jsonl"
    if os.path.exists(path):
        with open(path, "r") as f:
            lines = [json.loads(line) for line in f if line.strip()]
            return lines[-limit:] if len(lines) >= limit else lines 
    else: return {"message": "No DLQ log found"}

@app.get("/dlq_replayed")
def get_replayed_dlq_events(limit: int = 10):
    path = "/data/dlq_replayed.jsonl"
    if os.path.exists(path):
        with open(path, "r") as f:
            lines = [json.loads(line) for line in f if line.strip()]
            return lines[-limit:] if len(lines) >= limit else lines 
    else: return {"message": "No DLQ log found"}
