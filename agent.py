import time
import json
import threading
import requests
import psutil

with open("config.json") as f:
    CONFIG = json.load(f)

AGENT_NAME = CONFIG["agent_name"]
TOKEN = CONFIG["token"]
SERVER_URL = CONFIG["server_push_url"]
SITES = CONFIG["sites"]

def tester_site(url):
    t0 = time.time()
    try:
        r = requests.get(url, timeout=5)
        latency = round((time.time() - t0) * 1000, 2)
        status = "UP" if r.status_code == 200 else "DOWN"
    except Exception:
        latency = None
        status = "DOWN"

    return {"site": url, "status": status, "latency": latency}

def push_metrics(results):
    payload = {
        "token": TOKEN,
        "agent": AGENT_NAME,
        "cpu": psutil.cpu_percent(),
        "ram": psutil.virtual_memory().percent,
        "results": results
    }

    try:
        r = requests.post(SERVER_URL, json=payload, timeout=5)
        print(f"[PUSH] {r.status_code} → {r.text}")
    except Exception as e:
        print("[ERREUR PUSH]", e)

def monitoring_loop():
    while True:
        results = [tester_site(site) for site in SITES]
        push_metrics(results)
        time.sleep(10)

if __name__ == "__main__":
    print(f"[{AGENT_NAME}] Agent démarré.")
    threading.Thread(target=monitoring_loop, daemon=True).start()
    while True:
        time.sleep(1)
