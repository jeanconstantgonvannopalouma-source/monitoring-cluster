from flask import Flask, request, jsonify, render_template_string
import json
import os
import sqlite3

DB_FILE = "database.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Table des événements
    c.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            site TEXT,
            event TEXT,
            status TEXT,
            latency INTEGER,
            details TEXT
        )
    """)

    # Table des sites
    c.execute("""
        CREATE TABLE IF NOT EXISTS sites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE
        )
    """)

    conn.commit()
    conn.close()

# Initialisation au démarrage
init_db()

app = Flask(__name__)

LOG_FILE = "logs.jsonl"

TEMPLATE = """
<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <title>Monitoring Cluster</title>
  <style>
    body { font-family: sans-serif; background: #111; color: #eee; }
    h1 { text-align: center; }
    table { width: 100%; border-collapse: collapse; margin-top: 20px; }
    th, td { padding: 8px; border-bottom: 1px solid #444; text-align: left; }
    th { background: #222; }
    tr:nth-child(even) { background: #181818; }
    .up { color: #4caf50; }
    .down { color: #f44336; }
  </style>
</head>
<body>
  <h1>Monitoring Cluster - Dashboard</h1>
  <table>
    <tr>
      <th>Timestamp</th>
      <th>Site</th>
      <th>Event</th>
      <th>Status</th>
      <th>Latence (ms)</th>
      <th>Détails</th>
    </tr>
    {% for e in events %}
    <tr>
      <td>{{ e.timestamp }}</td>
      <td>{{ e.site }}</td>
      <td>{{ e.event }}</td>
      <td class="{{ 'up' if e.status == 'UP' else 'down' if e.status == 'DOWN' else '' }}">
        {{ e.status or '-' }}
      </td>
      <td>{{ e.latency if e.latency is not none else '-' }}</td>
      <td>{{ e.details }}</td>
    </tr>
    {% endfor %}
  </table>
</body>
</html>
"""
@app.route("/")
def home():
    return "Monitoring Cluster is running."

@app.route("/event", methods=["POST"])
def event():
    data = request.json

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("""
        INSERT INTO events (timestamp, site, event, status, latency, details)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        data.get("timestamp"),
        data.get("site"),
        data.get("event"),
        data.get("status"),
        data.get("latency"),
        json.dumps(data.get("details"))
    ))

    conn.commit()
    conn.close()

    return {"status": "ok"}

@app.route("/history")
def history():
    if not os.path.exists(LOG_FILE):
        return jsonify([])
    with open(LOG_FILE, "r") as f:
        lines = [json.loads(line) for line in f]
    return jsonify(lines)
@app.route("/dashboard")
def dashboard():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT timestamp, site, event, status, latency, details FROM events ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()

    events = []
    for r in rows:
        events.append({
            "timestamp": r[0],
            "site": r[1],
            "event": r[2],
            "status": r[3],
            "latency": r[4],
            "details": r[5]
        })

    return render_template_string(TEMPLATE, events=events)

# ---------------------------
# API SITES (version correcte)
# ---------------------------
@app.route("/api/sites", methods=["GET"])
def api_get_sites():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT url FROM sites")
    sites = [row[0] for row in c.fetchall()]
    conn.close()
    return jsonify(sites)

@app.route("/api/sites", methods=["POST"])
def api_add_site():
    data = request.json
    if "url" not in data:
        return {"error": "Missing 'url'"}, 400

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO sites (url) VALUES (?)", (data["url"],))
        conn.commit()
    except sqlite3.IntegrityError:
        return {"error": "Site already exists"}, 400
    finally:
        conn.close()

    return {"status": "added", "url": data["url"]}

@app.route("/api/sites/<path:url>", methods=["DELETE"])
def api_delete_site(url):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM sites WHERE url = ?", (url,))
    conn.commit()
    conn.close()
    return {"status": "deleted", "url": url}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
