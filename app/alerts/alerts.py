from typing import Dict, Any, List
from config import (
    ALERT_THRESHOLD_ERRORS,
    ALERT_THRESHOLD_ANOMALIES,
)
from predictor import predire_panne


def detect_alerts(history_events: List[Dict[str, Any]],
                  latest_results: List[Dict[str, Any]],
                  agents: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyse professionnelle pour déterminer si une alerte doit être déclenchée.

    Retourne :
    {
        "alerts": [...],
        "critical": True/False
    }
    """

    alerts = []

    # ============================
    #   1. ALERTES ERREURS
    # ============================

    errors = [e for e in history_events if e.get("type") == "ERROR"]

    if len(errors) >= ALERT_THRESHOLD_ERRORS:
        alerts.append({
            "type": "ERROR_SPIKE",
            "message": f"{len(errors)} erreurs détectées récemment",
            "severity": "HIGH"
        })

    # ============================
    #   2. ALERTES ANOMALIES
    # ============================

    anomalies = [e for e in history_events if e.get("type") == "ANOMALY"]

    if len(anomalies) >= ALERT_THRESHOLD_ANOMALIES:
        alerts.append({
            "type": "ANOMALY_SPIKE",
            "message": f"{len(anomalies)} anomalies détectées récemment",
            "severity": "MEDIUM"
        })

    # ============================
    #   3. ALERTES SITE DOWN
    # ============================

    for r in latest_results:
        status = r.get("status")
        if status == "ERROR" or (isinstance(status, int) and status >= 500):
            alerts.append({
                "type": "SITE_DOWN",
                "site": r.get("site"),
                "agent": r.get("agent"),
                "message": f"Site DOWN : {r.get('site')}",
                "severity": "CRITICAL"
            })

    # ============================
    #   4. ALERTES AGENT OFFLINE
    # ============================

    for agent in agents:
        if agent.get("status") == "OFFLINE":
            alerts.append({
                "type": "AGENT_OFFLINE",
                "agent": agent["name"],
                "message": f"Agent OFFLINE : {agent['name']}",
                "severity": "HIGH"
            })

    # ============================
    #   5. ALERTES RISQUE DE PANNE
    # ============================

    prediction = predire_panne(latest_results)

    if prediction["risque_global"] >= 60:
        alerts.append({
            "type": "HIGH_RISK",
            "message": f"Risque de panne élevé ({prediction['risque_global']}%)",
            "severity": "CRITICAL",
            "details": prediction
        })

    # ============================
    #   CRITICAL ?
    # ============================

    critical = any(a["severity"] == "CRITICAL" for a in alerts)

    return {
        "alerts": alerts,
        "critical": critical
    }
