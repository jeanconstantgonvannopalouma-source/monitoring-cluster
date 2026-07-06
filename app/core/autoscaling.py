from typing import Dict, Any, List
from statistics import mean

from predictor import predire_panne
from sre_module import analyser_performance_globale
from config import MONITOR_INTERVAL


# ============================
#   CONFIG AUTOSCALING INTERVAL
# ============================

MIN_INTERVAL = 5          # intervalle minimum (sec)
MAX_INTERVAL = 120        # intervalle maximum (sec)
STEP_UP = 10              # augmentation si stable
STEP_DOWN = 15            # réduction si instable


def calculer_intervalle_optimal(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calcule un intervalle de monitoring optimal basé sur :
    - latence
    - erreurs
    - anomalies
    - burn rate SRE
    - risque de panne (predictor)

    Retourne :
    {
        "intervalle": ...,
        "motifs": [...],
        "risque": ...,
        "sre": {...}
    }
    """

    motifs = []
    intervalle = MONITOR_INTERVAL

    if not results:
        return {
            "intervalle": intervalle,
            "motifs": ["Pas de données, intervalle inchangé"],
            "risque": 0,
            "sre": {}
        }

    # ============================
    #   ANALYSE SRE
    # ============================

    sre = analyser_performance_globale(results)

    latence_moyenne = sre.get("latence_moyenne") or 0
    erreur_rate = sre.get("erreur_rate") or 0
    burn_rate = sre.get("burn_rate") or 0

    # ============================
    #   ANALYSE RISQUE
    # ============================

    prediction = predire_panne(results)
    risque = prediction.get("risque_global", 0)

    # ============================
    #   LOGIQUE AUTOSCALING
    # ============================

    # 1. Si risque élevé → réduire intervalle
    if risque >= 60:
        intervalle = max(MIN_INTERVAL, intervalle - STEP_DOWN)
        motifs.append(f"Risque élevé ({risque}%), intervalle réduit")

    # 2. Si burn rate élevé → réduire intervalle
    elif burn_rate and burn_rate > 1.5:
        intervalle = max(MIN_INTERVAL, intervalle - STEP_DOWN)
        motifs.append(f"Burn rate élevé ({burn_rate}), intervalle réduit")

    # 3. Si latence élevée → réduire intervalle
    elif latence_moyenne > 1.5:
        intervalle = max(MIN_INTERVAL, intervalle - STEP_DOWN)
        motifs.append(f"Latence élevée ({latence_moyenne}s), intervalle réduit")

    # 4. Si erreurs fréquentes → réduire intervalle
    elif erreur_rate > 1.0:
        intervalle = max(MIN_INTERVAL, intervalle - STEP_DOWN)
        motifs.append(f"Taux d'erreurs élevé ({erreur_rate}%), intervalle réduit")

    # 5. Si tout est stable → augmenter intervalle
    else:
        intervalle = min(MAX_INTERVAL, intervalle + STEP_UP)
        motifs.append("Système stable, intervalle augmenté")

    # ============================
    #   RAPPORT FINAL
    # ============================

    return {
        "intervalle": intervalle,
        "motifs": motifs,
        "risque": risque,
        "sre": sre
    }
