import statistics
from logging.logger import log_event
from logging.history import ajouter_evenement

def score_site(result):
    """
    Calcule un score global pour un site.
    Plus le score est faible, meilleur est le site.
    """

    latence = result.get("latency") or 0
    status = result.get("status")
    dns = result.get("dns") or 0
    size = result.get("size") or 0
    anomalies = 1 if result.get("type") == "ANOMALY" else 0

    # Erreur HTTP → pénalité forte
    erreur = 1 if status not in (200, "OK") else 0

    # Score global
    score = (
        latence * 0.4 +
        erreur * 0.3 +
        anomalies * 0.2 +
        dns * 0.05 +
        size * 0.05
    )

    return score


def comparer_sites(resultats):
    """
    Comparaison professionnelle des sites.
    - score global
    - classement
    - top 5
    - bottom 5
    """

    if not resultats:
        return {
            "classement": [],
            "nb_sites": 0,
            "top_5": [],
            "bottom_5": []
        }

    # Calcul du score pour chaque site
    scored = []
    for r in resultats:
        scored.append({
            "site": r.get("site"),
            "agent": r.get("agent"),
            "latence": r.get("latency"),
            "status": r.get("status"),
            "dns": r.get("dns"),
            "size": r.get("size"),
            "score": score_site(r)
        })

    # Tri par score croissant
    classement = sorted(scored, key=lambda x: x["score"])

    # Logs
    log_event("INFO", "Comparaison des sites effectuée", "comparaison")

    # Historique
    ajouter_evenement("COMPARAISON", "cluster", "system", "Classement des sites mis à jour")

    return {
        "classement": classement,
        "nb_sites": len(resultats),
        "top_5": classement[:5],
        "bottom_5": classement[-5:]
    }
