import os
import requests
from datetime import date
import sqlite3

MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")
MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN")
MAILGUN_FROM = os.getenv("MAILGUN_FROM")
MAILGUN_TO = os.getenv("MAILGUN_TO")

def send_usage_report():
    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT api_key, endpoint, timestamp, success
        FROM api_usage
        WHERE date(timestamp) = ?
    """, (date.today().isoformat(),))
    logs = cursor.fetchall()
    conn.close()

    if not logs:
        return

    body = "\n".join([f"{l[0]} | {l[1]} | {l[2]} | {'✔' if l[3] else '❌'}" for l in logs])

    response = requests.post(
        f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
        auth=("api", MAILGUN_API_KEY),
        data={
            "from": MAILGUN_FROM,
            "to": MAILGUN_TO,
            "subject": f"Daily API Usage Report - {date.today()}",
            "text": body,
        },
    )
    print("Email sent:", response.status_code, response.text)

if __name__ == "__main__":
    send_usage_report()
