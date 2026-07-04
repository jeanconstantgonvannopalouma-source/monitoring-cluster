# anomalies.py

def detecter_anomalies(resultats):
    anomalies = []

    for r in resultats:
        if r.get("status") != 200:
            anomalies.append({
                "url": r["url"],
                "type": "HTTP_ERROR",
                "details": r.get("status")
            })
        if r.get("latence") and r["latence"] > 1.0:
            anomalies.append({
                "url": r["url"],
                "type": "HIGH_LATENCY",
                "details": r["latence"]
            })

    return anomalies
