from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import sqlite3
import os
import base64
import csv
from datetime import datetime
from fastapi.responses import FileResponse

admin_router = APIRouter()
security = HTTPBasic()

ADMIN_USER = os.getenv("ADMIN_USER")
ADMIN_PASS = os.getenv("ADMIN_PASS")

def check_auth(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = credentials.username == ADMIN_USER
    correct_password = credentials.password == ADMIN_PASS
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Basic"},
        )

@admin_router.get("/usage-logs", dependencies=[Depends(check_auth)])
def get_usage_logs():
    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()
    cursor.execute("SELECT api_key, endpoint, timestamp, success FROM api_usage ORDER BY timestamp DESC LIMIT 100")
    logs = cursor.fetchall()
    conn.close()
    return [{"api_key": log[0], "endpoint": log[1], "timestamp": log[2], "success": log[3]} for log in logs]

@admin_router.get("/export-usage", dependencies=[Depends(check_auth)])
def export_usage():
    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()
    cursor.execute("SELECT api_key, endpoint, timestamp, success FROM api_usage")
    logs = cursor.fetchall()
    conn.close()

    file_path = "usage_export.csv"
    with open(file_path, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["api_key", "endpoint", "timestamp", "success"])
        for log in logs:
            writer.writerow(log)
    return FileResponse(path=file_path, filename="usage_export.csv", media_type="text/csv")

@admin_router.get("/list-users", dependencies=[Depends(check_auth)])
def list_users():
    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()
    cursor.execute("SELECT label, api_key, active FROM api_users")
    users = cursor.fetchall()
    conn.close()
    return [{"label": user[0], "api_key": user[1], "active": bool(user[2])} for user in users]

@admin_router.post("/add-user", dependencies=[Depends(check_auth)])
def add_user(label: str, api_key: str):
    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO api_users (label, api_key, active) VALUES (?, ?, ?)", (label, api_key, 1))
    conn.commit()
    conn.close()
    return {"message": f"User '{label}' added successfully."}

@admin_router.post("/deactivate-user", dependencies=[Depends(check_auth)])
def deactivate_user(api_key: str):
    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE api_users SET active = 0 WHERE api_key = ?", (api_key,))
    conn.commit()
    conn.close()
    return {"message": f"User with key '{api_key}' deactivated."}

