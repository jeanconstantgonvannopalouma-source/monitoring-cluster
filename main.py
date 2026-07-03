import requests
import time

SERVER_URL = "https://monitoring-cluster-production.up.railway.app/event"
API_SITES = "https://monitoring-cluster-production.up.railway.app/api/sites"

def get_sites():
    """Récupère la liste des sites à tester depuis l'API."""
    try:
        r = requests.get(API_SITES, timeout=5)
        return r.json()
    except:
        return []

def send_event(event, details=None, status=None, latency=None, site=None):
    """Envoie un événement au serveur Flask."""
    payload = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "site": site,
        "event": event,
        "status": status,
        "latency": latency,
        "details": details
    }
    requests.post(SERVER_URL, json=payload)

def test_site(url):
    """Teste un site et envoie un événement UP/DOWN."""
    try:
        start = time.time()
        r = requests.get(url, timeout=5)
        latency = int((time.time() - start) * 1000)

        if r.status_code == 200:
            send_event("TEST", {"agent": "worker"}, "UP", latency, site=url)
        else:
            send_event("Site DOWN", f"Code HTTP {r.status_code}", "DOWN", latency, site=url)

    except Exception as e:
        send_event("Site DOWN", str(e), "DOWN", 0, site=url)

# Boucle principale
while True:
    sites = get_sites()
    if not sites:
        print("Aucun site à tester.")
    else:
        for site in sites:
            test_site(site)

    time.sleep(30)
