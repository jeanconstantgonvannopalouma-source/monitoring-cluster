from typing import List, Dict, Any
from statistics import mean


# ============================
#   CONFIG SRE (modifiable)
# ============================

SLO_DISPONIBILITE = 99.9        # Objectif de disponibilité
SLO_LATENCE_MS = 1.0            # Latence cible (1 sec)
SLO_ERREURS = 0.1               # 0.1% d'erreurs max


def percentile(values: List[float], p: float) -> float:
    """
    Calcule un percentile (p95, p99).
    """
    if not values:
        return None
    values_sorted = sorted(values)
    k = int(len(values_sorted) * p)
    k = min(k, len(values_sorted) - 1)
    return values_sorted[k]


def analyser_performance_globale(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyse SRE professionnelle basée sur les résultats des tests.

    Chaque entrée de `results` vient de monitor.py :
    {
        "site": ...,
        "agent": ...,
        "timestamp": ...,
        "status": ...,
        "latency": ...,
        "dns": ...,
        "size": ...,
        "error": ...
    }

    Retourne un rapport SRE structuré :
    {
        "disponibilite": ...,
        "latence_moyenne": ...,
        "latence_p95": ...,
        "latence_p99": ...,
        "erreur_rate": ...,
        "burn_rate": ...,
        "slo_status": ...,
        "score": ...
    }
    """

    if not results:
        return {
            "disponibilite": None,
            "latence_moyenne": None,
            "latence_p95": None,
            "latence_p99": None,
            "erreur_rate": None,
            "burn_rate": None,
            "slo_status": "NO_DATA",
            "score": 0
        }

    # ============================
    #   DISPONIBILITÉ
    # ============================

    total = len(results)
    up = sum(1 for r in results if isinstance(r.get("status"), int) and r["status"] < 500)
    disponibilite = (up / total) * 100 if total else 0

    # ============================
    #   LATENCE
    # ============================

    latences = [r["latency"] for r in results if r.get("latency") is not None]

    latence_moyenne = mean(latences) if latences else None
    latence_p95 = percentile(latences, 0.95)
    latence_p99 = percentile(latences, 0.99)

    # ============================
    #   TAUX D'ERREURS
    # ============================

    erreurs = sum(1 for r in results if r.get("status") == "ERROR")
    erreur_rate = (erreurs / total) * 100 if total else 0

    # ============================
    #   BURN RATE (SLO violation speed)
    # ============================

    # Burn rate = erreurs réelles / erreurs autorisées
    erreurs_autorisees = total * (SLO_ERREURS / 100)
    burn_rate = (erreurs / erreurs_autorisees) if erreurs_autorisees > 0 else None

    # ============================
    #   STATUT SLO
    # ============================

    slo_ok = (
        disponibilite >= SLO_DISPONIBILITE and
        (latence_moyenne is None or latence_moyenne <= SLO_LATENCE_MS) and
        erreur_rate <= SLO_ERREURS
    )

    slo_status = "OK" if slo_ok else "VIOLATED"

    # ============================
    #   SCORE GLOBAL SRE
    # ============================

    score = 0

    # Disponibilité
    if disponibilite is not None:
        score += min(disponibilite / SLO_DISPONIBILITE * 40, 40)

    # Latence
    if latence_moyenne is not None:
        score += max(0, 30 - (latence_moyenne * 10))

    # Erreurs
    score += max(0, 30 - erreur_rate * 5)

    score = round(score, 2)

    # ============================
    #   RAPPORT FINAL
    # ============================

    return {
        "disponibilite": round(disponibilite, 3),
        "latence_moyenne": latence_moyenne,
        "latence_p95": latence_p95,
        "latence_p99": latence_p99,
        "erreur_rate": round(erreur_rate, 3),
        "burn_rate": round(burn_rate, 3) if burn_rate is not None else None,
        "slo_status": slo_status,
        "score": score
    }
