import statistics
from logging.logger import log_event
from logging.history import ajouter_evenement

SLO = 0.99  # objectif interne
SLA = 0.98  # contrat externe

def analyser_performance_globale(resultats):
    """
    Analyse SRE professionnelle :
    - disponibilité
    - erreur budget
    - latence moyenne
    - variance latence
    - stabilité
    - taux d'erreurs
    - taux d'anomalies
    """

    if not resultats:
        return {
            "nb_sites": 0,
            "disponibilite": None,
            "erreur_budget": None,
            "latence_moyenne": None,
            "latence_variance": None,
            "stabilite": None,
            "taux_erreurs": None,
            "taux_anomalies": None,
            "slo": SLO,
            "sla": SLA
        }

    nb_total = len(resultats)
    nb_ok = sum(1 for r in resultats if r.get("status") == 200)
    nb_erreurs = nb_total - nb_ok

    # Disponibilité
    disponibilite = nb_ok / nb_total

    # Erreur budget
    erreur_budget = 1 - disponibilite

    # Latence
    latences = [r.get("latency") for r in resultats if r.get("latency")]
    latence_moyenne = statistics.mean(latences) if latences else None
    latence_variance = statistics.pvariance(latences) if len(latences) > 1 else 0

    # Stabilité (inverse de la variance)
    stabilite = 1 / (1 + latence_variance)

    # Anomalies
    anomalies = sum(1 for r in resultats if r.get("type") == "ANOMALY")
    taux_anomalies = anomalies / nb_total

    # Taux d'erreurs
    taux_erreurs = nb_erreurs / nb_total

    # Logs
    log_event("INFO", f"SRE → dispo={round(disponibilite,3)}, latence={latence_moyenne}", "sre_module")

    # Historique
    ajouter_evenement(
        "SRE",
        "cluster",
        "system",
        f"Dispo={round(disponibilite,3)}, Latence={latence_moyenne}"
    )

    return {
        "nb_sites": nb_total,
        "disponibilite": round(disponibilite, 3),
        "erreur_budget": round(erreur_budget, 3),
        "latence_moyenne": round(latence_moyenne, 3) if latence_moyenne else None,
        "latence_variance": round(latence_variance, 3),
        "stabilite": round(stabilite, 3),
        "taux_erreurs": round(taux_erreurs, 3),
        "taux_anomalies": round(taux_anomalies, 3),
        "slo": SLO,
        "sla": SLA
    }
