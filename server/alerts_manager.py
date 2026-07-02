from db import get_conn
from datetime import datetime

def add_alert(source, type_, details, owner_id, category="system"):
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        INSERT INTO alerts (source, type, details, owner_id, timestamp, category)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (source, type_, details, owner_id, datetime.now().isoformat(), category))

    conn.commit()
    conn.close()


def get_alerts(user_id):
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        SELECT id, source, type, details, timestamp, category
        FROM alerts
        WHERE owner_id = ?
        ORDER BY timestamp DESC
    """, (user_id,))

    rows = c.fetchall()
    conn.close()

    return [
        {
            "id": r[0],
            "source": r[1],
            "type": r[2],
            "details": r[3],
            "timestamp": r[4],
            "category": r[5]
        }
        for r in rows
    ]
