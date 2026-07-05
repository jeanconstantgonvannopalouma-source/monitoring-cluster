import requests
import time
import socket
from datetime import datetime

from config import TIMEOUT
from logging.logger import log_event
from logging.history import ajouter_evenement
from anomalies import detecter_anomalie


def resolve_dns(url):
    """Retourne le temps de résolution DNS."""
    try:
        debut = time.time()
        socket.gethostbyname(url.replace("https://", "").replace("http://", "").split("/")[0])
        return round(time.time() - debut, 3)
    except:
        return None


def tester_site(url, agent_name="agent-1"):
    """Teste un site et retourne un résultat professionnel."""
    result = {
        "site": url,
        "agent": agent_name,
        "timestamp": datetime.utcnow().isoformat(),
        "status": None,
        "latency": None,
        "dns": None,
        "size": None,
        "error": None
    }

    # DNS
    dns_time = resolve_dns(url)
    result["dns"] = dns_time

    try:
        debut = time.time()
        r = requests.get(url, timeout=TIMEOUT)
        latence = round(time.time() - debut, 3)

        result["status"] = r.status_code
        result["latency"] = latence
        result["size"] = len(r.content)

        # Historique
        ajouter_evenement("CHECK", url, agent_name, f"Status {r.status_code}, Latence {latence} ms")

        # Logs
        log_event("INFO", f"Test OK: {url} ({latence} ms)")

        # Anomalies
        anomaly = detecter_anomalie(result)
        if anomaly:
            ajouter_evenement("ANOMALY", url, agent_name, anomaly["type"])
            log_event("WARNING", f"Anomalie détectée sur {url}: {anomaly['type']}")

        return result

    except Exception as e:
        result["status"] = "ERROR"
        result["error"] = str(e)

        # Historique
        ajouter_evenement("ERROR", url, agent_name, str(e))

        # Logs
        log_event("ERROR", f"Erreur sur {url}: {e}")

        return result


def tester_tous_les_sites(sites, agent_name="agent-1"):
    """Teste tous les sites assignés à un agent."""
    resultats = []

    for site in sites:
        resultats.append(tester_site(site, agent_name))

    return resultats
