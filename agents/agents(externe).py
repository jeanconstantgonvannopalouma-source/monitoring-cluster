import requests
import time

SERVER_URL = "https://monitoring-cluster-production.up.railway.app/event"

def send_agent_event():
    payload = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "site": "agent",
        "event": "Heartbeat",
        "status": "OK",
        "details": {"agent": "local"}
    }
    requests.post(SERVER_URL, json=payload)

while True:
    send_agent_event()
    time.sleep(10)
