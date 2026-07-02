import time
import json
import threading
import requests
import psutil
import os
import sys
from flask import Flask, jsonify

app = Flask(__name__)

# ---------------------------------------------------------
# Chargement de la configuration
# ---------------------------------------------------------
with open("config.json") as f:
    CONFIG = json.load(f)

AGENT_NAME = CONFIG.get("agent_name", "Agent-Unknown")
AGENT_VERSION = CONFIG.get("version", "1.0")
UPDATE_URL = CONFIG.get("update_url", "")
SITES = CONFIG.get("sites", [])

SERVER_PUSH_URL = CONFIG.get("server_push_url", "http://localhost:5000/api/push")

# ---------------------------------------------------------
# Route : Ping (le serveur vérifie si l’agent est UP)
# ---------------------------------------------------------
@app.route("/ping")
def ping():
    return jsonify({
        "agent": AGENT_NAME,
        "status": "UP",
        "version": AGENT_VERSION,
        "timestamp": time.time()
    })

# ---------------------------------------------------------
# Route : Metrics (CPU, RAM, uptime)
# ---------------------------------------------------------
start_time = time.time()

@app.route("/metrics")
def metrics():
    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory().percent
    uptime = time.time() - start_time

    return jsonify({
        "agent": AGENT_NAME,
        "cpu": cpu,
        "ram": ram,
        "uptime": uptime
    })

# ---------------------------------------------------------
# Route : Sites surveillés par cet agent
# ---------------------------------------------------------
@app.route("/sites")
def sites():
    return jsonify({
        "agent": AGENT_NAME,
        "sites": SITES
    })

# ---------------------------------------------------------
# Route : Ping entre agents (réseau interne du cluster)
# ---------------------------------------------------------
@app.route("/ping_agent/<name>")
def ping_agent(name):
    return jsonify({
        "from": AGENT_NAME,
        "to": name,
        "status": "ok",
        "latency": 0
    })

# ---------------------------------------------------------
# Route : Version actuelle (pour auto-update)
# ---------------------------------------------------------
@app.route("/check_update")
def check_update():
    return jsonify({
        "agent": AGENT_NAME,
        "version": AGENT_VERSION
    })

# ---------------------------------------------------------
# Fonction : Test d’un site
# ---------------------------------------------------------
def tester_site(url):
    t0 = time.time()
    try:
        r = requests.get(url, timeout=5)
        latency = round((time.time() - t0) * 1000, 2)
        status = "UP" if r.status_code == 200 else "DOWN"
    except Exception:
        latency = None
        status = "DOWN"

    return {
        "site": url,
        "status": status,
        "latency": latency,
        "timestamp": time.time(),
        "agent": AGENT_NAME
    }

# ---------------------------------------------------------
# Fonction : Envoi des résultats au serveur
# ---------------------------------------------------------
def push_result(result):
    try:
        requests.post(SERVER_PUSH_URL, json=result, timeout=3)
    except:
        pass

# ---------------------------------------------------------
# Boucle de monitoring des sites
# ---------------------------------------------------------
def monitoring_loop():
    while True:
        for site in SITES:
            result = tester_site(site)
            push_result(result)
        time.sleep(10)  # intervalle de scan

threading.Thread(target=monitoring_loop, daemon=True).start()

# ---------------------------------------------------------
# Fonction : Appliquer une mise à jour
# ---------------------------------------------------------
def apply_update():
    try:
        r = requests.get(UPDATE_URL, timeout=5)
        if r.status_code != 200:
            return

        new_code = r.text

        # Écrire le nouveau fichier
        with open("agent_new.py", "w") as f:
            f.write(new_code)

        # Remplacer l’ancien fichier
        os.replace("agent_new.py", "agent.py")

        # Redémarrer l’agent
        os.execv(sys.executable, ['python'] + sys.argv)

    except Exception as e:
        print("Erreur update :", e)

# ---------------------------------------------------------
# Boucle de vérification des mises à jour
# ---------------------------------------------------------
def update_loop():
    while True:
        try:
            r = requests.get(UPDATE_URL, timeout=5)
            if r.status_code == 200:
                apply_update()
        except:
            pass

        time.sleep(30)

threading.Thread(target=update_loop, daemon=True).start()

# ---------------------------------------------------------
# Lancement de l’agent
# ---------------------------------------------------------
if __name__ == "__main__":
    print(f"[{AGENT_NAME}] Agent démarré. Version {AGENT_VERSION}")
    app.run(host="0.0.0.0", port=5000)
