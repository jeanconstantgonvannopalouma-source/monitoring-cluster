import requests
import time

SERVER_URL = "https://monitoring-cluster-production.up.railway.app/event"
SITE_TO_TEST = "https://google.com"

def send_event(event, details=None, status=None, latency=None):
    payload = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "site": SITE_TO_TEST,
        "event": event,
        "status": status,
        "latency": latency,
        "details": details
    }
    requests.post(SERVER_URL, json=payload)

def test_site():
    try:
        start = time.time()
        r = requests.get(SITE_TO_TEST, timeout=5)
        latency = int((time.time() - start) * 1000)

        if r.status_code == 200:
            send_event("TEST", {"agent": "worker"}, "UP", latency)
        else:
            send_event("Site DOWN", f"Code HTTP {r.status_code}", "DOWN", latency)

    except Exception as e:
        send_event("Site DOWN", str(e), "DOWN", 0)

while True:
    test_site()
    time.sleep(30)
