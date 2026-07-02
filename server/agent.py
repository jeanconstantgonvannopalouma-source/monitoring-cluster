import json
import time
import requests
import socket
from datetime import datetime
import psutil

# ---------------------------------------------------------
# CHARGER LA CONFIGURATION
# ---------------------------------------------------------

try:
    with open("config.json", "r") as f:
        CONFIG = json.load(f)
except FileNotFoundError:
    print("ERREUR : config.json introuvable !")
    print("Crée un fichier config.json contenant :")
    print('{ "server": "http://127.0.0.1:5000", "token": "" }')
    exit()

SERVER = CONFIG.get("server", "http://127.0.0.1:5000")
TOKEN = CONFIG.get("token", "")

if not TOKEN.strip():
    print("ERREUR : Aucun token valide dans config.json !")
    print("Va sur ton SaaS → /api/token → copie le token dans config.json.")
    exit()

# ---------------------------------------------------------
# IDENTITÉ DE L’AGENT
# ---------------------------------------------------------

AGENT_NAME = socket.gethostname()
AGENT_IP = socket.gethostbyname(socket.gethostname())
START_TIME = time.time()

# ---------------------------------------------------------
# ENREGISTREMENT AUTOMATIQUE DE L’AGENT
# ---------------------------------------------------------

def register_agent():
    url = f"{SERVER}/api/agent"

    data = {
        "agent": AGENT_NAME,
        "ip": AGENT_IP,
        "token": TOKEN,
        "timestamp": datetime.now().isoformat()
    }

    try:
        r = requests.post(url, json=data, timeout=5)
        print("Enregistrement agent :", r.json())
    except Exception as e:
        print("Erreur enregistrement agent :", e)

# ---------------------------------------------------------
# TEST DES SITES
# ---------------------------------------------------------

def tester_site(url):
    start = time.time()

    try:
        r = requests.get(url, timeout=5)
        latency = int((time.time() - start) * 1000)

        status = "UP" if 200 <= r.status_code < 400 else "DOWN"

        return {
            "site": url,
            "status": status,
            "latency": latency,
            "agent": AGENT_NAME,
            "category": "default"
        }

    except Exception:
        return {
            "site": url,
            "status": "DOWN",
            "latency": 0,
            "agent": AGENT_NAME,
            "category": "default"
        }

def charger_sites():
    sites = []

    try:
        with open("sites.jsonl", "r") as f:
            for line in f:
                try:
                    sites.append(json.loads(line)["site"])
                except:
                    pass
    except FileNotFoundError:
        sites = [
            "https://google.com",
            "https://github.com",
            "https://openai.com"
        ]

    return sites

# ---------------------------------------------------------
# METRIQUES CPU / RAM / UPTIME
# ---------------------------------------------------------

def collect_metrics():
    return {
        "agent": AGENT_NAME,
        "ip": AGENT_IP,
        "cpu": psutil.cpu_percent(),
        "ram": psutil.virtual_memory().percent,
        "uptime": time.time() - START_TIME,
        "timestamp": datetime.now().isoformat()
    }

# ---------------------------------------------------------
# ENVOI AU SERVEUR
# ---------------------------------------------------------

def envoyer_rapport(data):
    url = f"{SERVER}/metrics"

    try:
        r = requests.post(url, json=data, timeout=5)
        print("Metrics envoyées :", r.json())
    except Exception as e:
        print("Erreur envoi metrics :", e)

# ---------------------------------------------------------
# BOUCLE PRINCIPALE
# ---------------------------------------------------------

def boucle_agent():
    print(f"Agent SaaS démarré : {AGENT_NAME} ({AGENT_IP})")
    print("Enregistrement auprès du serveur…")

    register_agent()

    while True:
        sites = charger_sites()
        resultats = [tester_site(s) for s in sites]

        metrics = collect_metrics()

        payload = {
            "agent": AGENT_NAME,
            "ip": AGENT_IP,
            "timestamp": metrics["timestamp"],
            "cpu": metrics["cpu"],
            "ram": metrics["ram"],
            "uptime": metrics["uptime"],
            "results": resultats,
            "token": TOKEN
        }

        envoyer_rapport(payload)

        time.sleep(10)

# ---------------------------------------------------------
# LANCEMENT
# ---------------------------------------------------------

if __name__ == "__main__":
    boucle_agent()
