from fastapi import FastAPI, Request, Header, HTTPException
from admin import admin_router
import sqlite3
from datetime import datetime
import os

app = FastAPI()

API_KEYS = {"demo-key-123"}

@app.middleware("http")
async def check_api_key(request: Request, call_next):
    if request.url.path.startswith("/api"):
        api_key = request.headers.get("x-api-key")
        if not api_key or api_key not in API_KEYS:
            raise HTTPException(status_code=401, detail="Invalid API key.")
        log_api_usage(api_key, request.url.path)
    response = await call_next(request)
    return response

@app.get("/api/covered-calls/generate")
def generate_trade():
    return {"message": "Covered call recommendation would be generated here."}

def log_api_usage(api_key, endpoint):
    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS api_usage (api_key TEXT, endpoint TEXT, timestamp TEXT, success INTEGER)")
    cursor.execute("INSERT INTO api_usage VALUES (?, ?, ?, ?)", (api_key, endpoint, datetime.now().isoformat(), 1))
    conn.commit()
    conn.close()

app.include_router(admin_router, prefix="/admin")

