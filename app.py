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

# ---------------------------
# TEMPLATE HTML DU DASHBOARD
# ---------------------------

TEMPLATE = """
<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <title>Monitoring Cluster</title>

  <!-- Chart.js -->
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

  <style>
    body { font-family: sans-serif; background: #111; color: #eee; }
    h1 { text-align: center; }
    h2 { margin-top: 40px; }
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

  <h2>Latence dans le temps</h2>
  <canvas id="latencyChart" width="400" height="150"></canvas>

  <h2>Statut UP/DOWN dans le temps</h2>
  <canvas id="statusChart" width="400" height="150"></canvas>

  <h2>Disponibilité par site</h2>
  <canvas id="availabilityChart" width="400" height="150"></canvas>

  <h2>Métriques</h2>
  <table>
    <tr>
      <th>Site</th>
      <th>Disponibilité (%)</th>
      <th>Latence moyenne (ms)</th>
      <th>Taux d’erreur (%)</th>
      <th>Stabilité</th>
    </tr>
    {% for m in metrics %}
    <tr>
      <td>{{ m.site }}</td>
      <td>{{ m.availability }}</td>
      <td>{{ m.avg_latency }}</td>
      <td>{{ m.error_rate }}</td>
      <td>{{ m.stability }}</td>
    </tr>
    {% endfor %}
  </table>

  <h2>Historique des événements</h2>
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

  <!-- Script des graphiques -->
  <script>
    const latencyData = {{ latency_data | safe }};
    const statusData = {{ status_data | safe }};
    const availabilityData = {{ availability_chart_data | safe }};

    // Latence
    const latencyLabels = latencyData.map(e => e.timestamp);
    const latencies = latencyData.map(e => e.latency);

    const latencyCtx = document.getElementById('latencyChart').getContext('2d');
    new Chart(latencyCtx, {
      type: 'line',
      data: {
        labels: latencyLabels,
        datasets: [{
          label: 'Latence (ms)',
          data: latencies,
          borderColor: 'rgba(75, 192, 192, 1)',
          backgroundColor: 'rgba(75, 192, 192, 0.2)',
          borderWidth: 2,
          tension: 0.3
        }]
      },
      options: {
        scales: {
          y: { beginAtZero: true }
        }
      }
    });

    // UP/DOWN
    const statusLabels = statusData.map(e => e.timestamp);
    const statusValues = statusData.map(e => e.status_value);

    const statusCtx = document.getElementById('statusChart').getContext('2d');
    new Chart(statusCtx, {
      type: 'bar',
      data: {
        labels: statusLabels,
        datasets: [{
          label: 'Status (1 = UP, 0 = DOWN)',
          data: statusValues,
          backgroundColor: statusValues.map(v => v === 1 ? 'rgba(76, 175, 80, 0.7)' : 'rgba(244, 67, 54, 0.7)')
        }]
      },
      options: {
        scales: {
          y: { beginAtZero: true, max: 1 }
        }
      }
    });

    // Disponibilité par site
    const availabilityLabels = availabilityData.map(e => e.site);
    const availabilityValues = availabilityData.map(e => e.availability);

    const availabilityCtx = document.getElementById('availabilityChart').getContext('2d');
    new Chart(availabilityCtx, {
      type: 'bar',
      data: {
        labels: availabilityLabels,
        datasets: [{
          label: 'Disponibilité (%)',
          data: availabilityValues,
          backgroundColor: 'rgba(33, 150, 243, 0.7)'
        }]
      },
      options: {
        scales: {
          y: { beginAtZero: true, max: 100 }
        }
      }
    });
  </script>

</body>
</html>
"""

# ---------------------------
# ROUTES DE BASE
# ---------------------------

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

# ---------------------------
# API SITES
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

# ---------------------------
# API METRICS
# ---------------------------

@app.route("/api/metrics/<path:url>", methods=["GET"])
def api_metrics(url):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("""
        SELECT status, latency FROM events
        WHERE site = ?
    """, (url,))
    rows = c.fetchall()

    conn.close()

    if not rows:
        return jsonify({
            "site": url,
            "availability": 0,
            "avg_latency": None,
            "error_rate": 0,
            "stability": "No data"
        })

    total = len(rows)
    up = sum(1 for r in rows if r[0] == "UP")
    down = sum(1 for r in rows if r[0] == "DOWN")

    latencies = [r[1] for r in rows if r[1] is not None]
    avg_latency = sum(latencies) / len(latencies) if latencies else None

    availability = round((up / total) * 100, 2)
    error_rate = round((down / total) * 100, 2)

    last10 = rows[-10:]
    up10 = sum(1 for r in last10 if r[0] == "UP")
    down10 = sum(1 for r in last10 if r[0] == "DOWN")

    if up10 >= 7:
        stability = "Stable"
    elif down10 >= 5:
        stability = "Unstable"
    else:
        stability = "Fluctuating"

    return jsonify({
        "site": url,
        "availability": availability,
        "avg_latency": avg_latency,
        "error_rate": error_rate,
        "stability": stability
    })

# ---------------------------
# DASHBOARD
# ---------------------------

@app.route("/dashboard")
def dashboard():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("SELECT timestamp, site, event, status, latency, details FROM events ORDER BY id DESC")
    rows = c.fetchall()

    events = []
    latency_data = []
    status_data = []
    for r in rows:
        events.append({
            "timestamp": r[0],
            "site": r[1],
            "event": r[2],
            "status": r[3],
            "latency": r[4],
            "details": r[5]
        })

        latency_data.append({
            "timestamp": r[0],
            "latency": r[4]
        })

        status_value = 1 if r[3] == "UP" else 0
        status_data.append({
            "timestamp": r[0],
            "status_value": status_value
        })

    c.execute("SELECT url FROM sites")
    sites = [row[0] for row in c.fetchall()]

    conn.close()

    metrics = []
    availability_chart_data = []
    for site in sites:
        m = api_metrics(site).json
        metrics.append(m)
        availability_chart_data.append({
            "site": m["site"],
            "availability": m["availability"]
        })

    return render_template_string(
        TEMPLATE,
        events=events,
        metrics=metrics,
        latency_data=json.dumps(latency_data),
        status_data=json.dumps(status_data),
        availability_chart_data=json.dumps(availability_chart_data)
    )

# ---------------------------
# LANCEMENT SERVEUR
# ---------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
