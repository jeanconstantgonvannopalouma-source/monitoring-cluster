from flask import Flask, request, jsonify, render_template_string
import json
import os

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
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(data) + "\n")
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
    events = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            for line in f:
                try:
                    e = json.loads(line)
                    events.append(e)
                except:
                    continue
    return render_template_string(TEMPLATE, events=events)

@app.route("/api/sites", methods=["GET"])
def api_get_sites():
    if not os.path.exists("sites.json"):
        return jsonify([])
    with open("sites.json", "r") as f:
        return jsonify(json.load(f))

@app.route("/api/sites", methods=["POST"])
def api_add_site():
    data = request.json
    if "url" not in data:
        return {"error": "Missing 'url'"}, 400

    sites = []
    if os.path.exists("sites.json"):
        with open("sites.json", "r") as f:
            sites = json.load(f)

    sites.append(data["url"])

    with open("sites.json", "w") as f:
        json.dump(sites, f)

    return {"status": "added", "url": data["url"]}

@app.route("/api/sites/<path:url>", methods=["DELETE"])
def api_delete_site(url):
    if not os.path.exists("sites.json"):
        return {"error": "No sites"}, 404

    with open("sites.json", "r") as f:
        sites = json.load(f)

    if url not in sites:
        return {"error": "Site not found"}, 404

    sites.remove(url)

    with open("sites.json", "w") as f:
        json.dump(sites, f)

    return {"status": "deleted", "url": url}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
@app.route("/api/sites", methods=["GET"])
def api_get_sites():
    if not os.path.exists("sites.json"):
        return jsonify([])
    with open("sites.json", "r") as f:
        return jsonify(json.load(f))

@app.route("/api/sites", methods=["POST"])
def api_add_site():
    data = request.json
    if "url" not in data:
        return {"error": "Missing 'url'"}, 400

    sites = []
    if os.path.exists("sites.json"):
        with open("sites.json", "r") as f:
            sites = json.load(f)

    sites.append(data["url"])

    with open("sites.json", "w") as f:
        json.dump(sites, f)

    return {"status": "added", "url": data["url"]}

@app.route("/api/sites/<path:url>", methods=["DELETE"])
def api_delete_site(url):
    if not os.path.exists("sites.json"):
        return {"error": "No sites"}, 404

    with open("sites.json", "r") as f:
        sites = json.load(f)

    if url not in sites:
        return {"error": "Site not found"}, 404

    sites.remove(url)

    with open("sites.json", "w") as f:
        json.dump(sites, f)

    return {"status": "deleted", "url": url}
