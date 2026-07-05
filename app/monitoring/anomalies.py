import time
from datetime import datetime
from config import (
    ANOMALY_LATENCY_THRESHOLD,
    ANOMALY_DNS_THRESHOLD,
    ANOMALY_SIZE_THRESHOLD,
    ANOMALY_UNSTABLE_THRESHOLD
)

def detecter_anomalie(result):
    """Détecte une anomalie sur un seul site."""
    anomalies = []

    url = result.get("site")
    agent = result.get("agent")
    latence = result.get("latency")
    dns = result.get("dns")
    size = result.get("size")
    status = result.get("status")

    timestamp = datetime.utcnow().isoformat()

    # Erreur HTTP
    if status != 200:
        anomalies.append({
            "site": url,
            "agent": agent,
            "type": "HTTP_ERROR",
            "level": "HIGH",
            "metric": status,
            "timestamp": timestamp
        })

    # Latence élevée
    if latence and latence > ANOMALY_LATENCY_THRESHOLD:
        anomalies.append({
            "site": url,
            "agent": agent,
            "type": "HIGH_LATENCY",
            "level": "MEDIUM" if latence < 2 else "HIGH",
            "metric": latence,
            "timestamp": timestamp
        })

    # DNS lent
    if dns and dns > ANOMALY_DNS_THRESHOLD:
        anomalies.append({
            "site": url,
            "agent": agent,
            "type": "SLOW_DNS",
            "level": "MEDIUM",
            "metric": dns,
            "timestamp": timestamp
        })

    # Taille de réponse anormale
    if size and size > ANOMALY_SIZE_THRESHOLD:
        anomalies.append({
            "site": url,
            "agent": agent,
            "type": "LARGE_RESPONSE",
            "level": "LOW",
            "metric": size,
            "timestamp": timestamp
        })

    return anomalies


def detecter_anomalies(resultats):
    """Détecte les anomalies sur tous les sites."""
    anomalies = []

    for r in resultats:
        anomalies.extend(detecter_anomalie(r))

    return anomalies
