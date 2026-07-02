import time
from agents import get_agents, update_agent
from history import ajouter_evenement
from logger import log_event
from alert_manager import alerte
from config import INTERVAL_MIN, INTERVAL_MAX


def autoscaling():
    """
    Ajuste automatiquement la fréquence de monitoring selon la charge du cluster.
    Envoie des alertes lors des changements de capacité.
    """

    agents = get_agents()

    if not agents:
        return INTERVAL_MAX  # aucun agent → on ralentit

    # Calcul du taux d'agents UP
    nb_agents = len(agents)
    nb_up = sum(1 for a in agents.values() if a["status"] == "UP")
    taux_up = nb_up / nb_agents

    # Calcul de la charge moyenne CPU/RAM
    cpu_vals = [a["cpu"] for a in agents.values() if a["cpu"] is not None]
    ram_vals = [a["ram"] for a in agents.values() if a["ram"] is not None]

    cpu_moy = sum(cpu_vals) / len(cpu_vals) if cpu_vals else 0
    ram_moy = sum(ram_vals) / len(ram_vals) if ram_vals else 0

    # ------------------------------
    # LOGIQUE D'AUTOSCALING
    # ------------------------------

    # Cas 1 : surcharge → SCALE UP
    if taux_up < 0.5 or cpu_moy > 80 or ram_moy > 80:
        interval = INTERVAL_MIN

        alerte(
            "CLUSTER",
            "SCALE UP",
            f"Agents UP: {nb_up}/{nb_agents}, CPU moy: {cpu_moy}%, RAM moy: {ram_moy}%"
        )

        ajouter_evenement(
            "CLUSTER",
            "SCALE_UP",
            f"Charge élevée → interval = {INTERVAL_MIN}s"
        )

        log_event(
            "CLUSTER",
            "SCALE UP",
            details=f"Interval réduit à {INTERVAL_MIN}s"
        )

        return interval

    # Cas 2 : cluster stable → SCALE DOWN
    if taux_up == 1 and cpu_moy < 40 and ram_moy < 40:
        interval = INTERVAL_MAX

        alerte(
            "CLUSTER",
            "SCALE DOWN",
            f"Agents UP: {nb_up}/{nb_agents}, CPU moy: {cpu_moy}%, RAM moy: {ram_moy}%"
        )

        ajouter_evenement(
            "CLUSTER",
            "SCALE_DOWN",
            f"Charge faible → interval = {INTERVAL_MAX}s"
        )

        log_event(
            "CLUSTER",
            "SCALE DOWN",
            details=f"Interval augmenté à {INTERVAL_MAX}s"
        )

        return interval

    # Cas 3 : état normal → interval moyen
    interval = (INTERVAL_MIN + INTERVAL_MAX) // 2

    log_event(
        "CLUSTER",
        "SCALE NORMAL",
        details=f"Interval = {interval}s"
    )

    return interval
def calculer_intervalle_optimal(cluster):
    """
    Retourne un intervalle de monitoring optimal basé sur la charge du cluster.
    Pour l'instant : version simple.
    """
    try:
        cpu = cluster.get("cpu_moy", 0)
        ram = cluster.get("ram_moy", 0)

        # Exemple simple : plus la charge est haute, plus on réduit l'intervalle
        if cpu > 80 or ram > 80:
            return 5
        if cpu > 50 or ram > 50:
            return 10
        return 20

    except Exception:
        return 20
