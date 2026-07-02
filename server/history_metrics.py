import json
from datetime import datetime

def charger_metrics():
    metrics = []

    try:
        with open("agent_metrics.jsonl", "r") as f:
            for line in f:
                try:
                    metrics.append(json.loads(line))
                except:
                    pass
    except FileNotFoundError:
        return []

    # Tri par date
    metrics = sorted(metrics, key=lambda x: x.get("timestamp", ""), reverse=True)
    return metrics


def extraire_latence_moyenne(metrics):
    points = []
    for m in metrics:
        results = m.get("results", [])
        latences = [r.get("latency") for r in results if r.get("latency") is not None]
        if latences:
            points.append({
                "timestamp": m.get("timestamp"),
                "latency": sum(latences) / len(latences)
            })
    return points


def extraire_disponibilite(metrics):
    points = []
    for m in metrics:
        results = m.get("results", [])
        up = sum(1 for r in results if r.get("status") == "UP")
        down = sum(1 for r in results if r.get("status") == "DOWN")
        total = len(results)

        if total > 0:
            dispo = (up / total) * 100
            points.append({
                "timestamp": m.get("timestamp"),
                "dispo": dispo
            })
    return points


def extraire_uptime(metrics):
    return [
        {"timestamp": m.get("timestamp"), "uptime": m.get("uptime", 0)}
        for m in metrics
    ]


def extraire_anomalies(metrics):
    points = []
    for m in metrics:
        results = m.get("results", [])
        anomalies = sum(1 for r in results if r.get("status") == "DOWN")
        points.append({
            "timestamp": m.get("timestamp"),
            "anomalies": anomalies
        })
    return points
