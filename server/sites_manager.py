from db import get_conn
from datetime import datetime

def add_site(url, user_id):
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        INSERT INTO sites (url, owner_id, created_at)
        VALUES (?, ?, ?)
    """, (url, user_id, datetime.now().isoformat()))

    conn.commit()
    conn.close()


def get_sites(user_id):
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        SELECT id, url, created_at
        FROM sites
        WHERE owner_id = ?
    """, (user_id,))

    rows = c.fetchall()
    conn.close()

    return [{"id": r[0], "url": r[1], "created_at": r[2]} for r in rows]
