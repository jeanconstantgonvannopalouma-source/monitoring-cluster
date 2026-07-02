import requests
import time
import csv
from datetime import datetime

from anomalies import AnomalyDetector
from history import ajouter_evenement
from logger import log_event
from alert_manager import alerte
from config import FICHIER_LOG, DEFAULT_CATEGORY

detector = AnomalyDetector()


def tester_site(url, category=DEFAULT_CATEGORY, agent="server"):
    """
    Teste un site : temps de réponse + statut UP/DOWN.
    Enregistre :
    - CSV principal
    - logs.jsonl
    - history.jsonl
    - anomalies live
    - alertes email + telegram
    """

    start = time.time()

    try:
        response = requests.get(url, timeout=5)
        status = "UP" if response.status_code == 200 else "DOWN"
    except Exception:
        status = "DOWN"

    end = time.time()
    response_time_ms = int((end - start) * 1000)

    # Détection d'anomalies live
    detector.add_response_time(url, response_time_ms)
    detector.add_status(url, status)

    # Historique des pannes
    if status == "DOWN":
        ajouter_evenement(url, "DOWN", "Le site ne répond plus")
        alerte(url, "Site DOWN", f"Temps de réponse : {response_time_ms} ms")
    else:
        ajouter_evenement(url, "UP", "Le site répond correctement")

    # Log avancé
    log_event(
        site=url,
        event="TEST",
        status=status,
        latency=response_time_ms,
        details={"agent": agent}
    )

    # Écriture dans le CSV principal
    with open(FICHIER_LOG, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            url,
            status,
            response_time_ms,
            agent,
            category
        ])

    return {
        "site": url,
        "status": status,
        "latency": response_time_ms,
        "agent": agent,
        "category": category
    }


def tester_tous_les_sites():
    """
    Teste tous les sites présents dans le fichier CSV.
    """

    sites = ["http://google.com"]

    try:
        with open(FICHIER_LOG, "r") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:
                    sites.append(row[1])
    except FileNotFoundError:
        return []

    sites = sorted(set(sites))

    resultats = []
    for site in sites:
        info = tester_site(site)
        resultats.append(info)

    return resultats


def get_anomalies():
    return detector.get_latest_anomalies()
