import requests
import time
import socket
from datetime import datetime

from config import TIMEOUT

# Import corrects (ton app.py utilise ces modules à la racine)
from logger import log_event
from history import ajouter_evenement
from anomalies import detecter_anomalie


def resolve_dns(url):
    """
    Mesure le temps de résolution DNS.
    Retourne un float en secondes ou None si échec.
    """
    try:
        debut = time.time()
        hostname = url.replace("https://", "").replace("http://", "").split("/")[0]
        socket.gethostbyname(hostname)
        return round(time.time() - debut, 3)
    except Exception:
        return None


def tester_site(url, agent_name="agent-1"):
    """
    Test professionnel d’un site :
    - DNS
    - Latence HTTP
    - Taille de la réponse
    - Code HTTP
    - Détection d’anomalies
    - Historique
    - Logs
    """

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
        ajouter_evenement(
            type_event="CHECK",
            site=url,
            agent=agent_name,
            details=f"Status {r.status_code}, Latence {latence} sec"
        )

        # Logs
        log_event("INFO", f"[{agent_name}] Test OK: {url} ({latence} sec)")

        # Détection d’anomalies
        anomaly = detecter_anomalie(result)
        if anomaly:
            ajouter_evenement(
                type_event="ANOMALY",
                site=url,
                agent=agent_name,
                details=anomaly["type"]
            )
            log_event("WARNING", f"[{agent_name}] Anomalie détectée sur {url}: {anomaly['type']}")

        return result

    except Exception as e:
        result["status"] = "ERROR"
        result["error"] = str(e)

        # Historique
        ajouter_evenement(
            type_event="ERROR",
            site=url,
            agent=agent_name,
            details=str(e)
        )

        # Logs
        log_event("ERROR", f"[{agent_name}] Erreur sur {url}: {e}")

        return result


def tester_tous_les_sites(sites, agent_name="agent-1"):
    """
    Teste tous les sites assignés à un agent.
    Retourne une liste de résultats professionnels.
    """
    resultats = []

    for site in sites:
        resultats.append(tester_site(site, agent_name))

    return resultats
