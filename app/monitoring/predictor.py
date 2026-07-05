import statistics
from logging.logger import log_event
from logging.history import ajouter_evenement

def predire_panne(historique):
    """
    Prédiction professionnelle basée sur :
    - erreurs HTTP
    - latence
    - anomalies
    - disponibilité
    - stabilité réseau
    """

    if not historique:
        return {
            "prediction": "Aucune donnée",
            "risque": 0,
            "details": "Pas assez d'événements pour analyser"
        }

    # Erreurs HTTP
    erreurs = sum(1 for e in historique if e.get("status") not in (200, "OK"))
    total = len(historique)
    taux_erreurs = erreurs / total

    # Latence
    latences = [e.get("latency") for e in historique if e.get("latency")]
    latence_moyenne = statistics.mean(latences) if latences else None
    latence_variance = statistics.pvariance(latences) if len(latences) > 1 else 0

    # Anomalies
    anomalies = sum(1 for e in historique if e.get("type") == "ANOMALY")
    taux_anomalies = anomalies / total

    # Disponibilité
    dispo_events = [e for e in historique if e.get("status") == 200]
    disponibilite = len(dispo_events) / total

    # Score global
    score = 0

    score += taux_erreurs * 0.4
    score += taux_anomalies * 0.3
    score += (latence_moyenne or 0) * 0.2
    score += latence_variance * 0.1
    score += (1 - disponibilite) * 0.3

    # Interprétation
    if score < 0.2:
        prediction = "Risque faible"
    elif score < 0.5:
        prediction = "Risque moyen"
    elif score < 0.8:
        prediction = "Risque élevé"
    else:
        prediction = "Panne imminente"

    # Logs
    log_event("INFO", f"Prédiction générée : {prediction} (score={round(score,2)})", "predictor")

    # Historique
    ajouter_evenement("PREDICTION", "cluster", "system", f"{prediction} (score={round(score,2)})")

    return {
        "prediction": prediction,
        "risque": round(score, 2),
        "details": {
            "taux_erreurs": round(taux_erreurs, 2),
            "latence_moyenne": round(latence_moyenne, 3) if latence_moyenne else None,
            "latence_variance": round(latence_variance, 3),
            "taux_anomalies": round(taux_anomalies, 2),
            "disponibilite": round(disponibilite, 2)
        }
    }
