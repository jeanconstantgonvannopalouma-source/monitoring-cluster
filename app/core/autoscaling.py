from config import INTERVAL_MIN, INTERVAL_MAX
from logging.logger import log_event
from logging.history import ajouter_evenement

def calculer_intervalle_optimal(metrics, anomalies, agents):
    """
    Calcule un intervalle intelligent basé sur :
    - latence moyenne
    - disponibilité
    - anomalies
    - CPU / RAM des agents
    - stabilité
    """

    latence = metrics.get("latence_moyenne")
    dispo = metrics.get("dispo")
    uptime = metrics.get("uptime")

    nb_anomalies = len(anomalies)

    cpu_moyen = sum(a["cpu"] for a in agents if a["cpu"] is not None) / len(agents)
    ram_moyenne = sum(a["ram"] for a in agents if a["ram"] is not None) / len(agents)

    # Base
    intervalle = INTERVAL_MAX

    # Latence
    if latence is not None:
        if latence < 0.1:
            intervalle -= 40
        elif latence < 0.3:
            intervalle -= 20
        else:
            intervalle += 20

    # Disponibilité
    if dispo is not None:
        if dispo < 95:
            intervalle += 20
        elif dispo > 99:
            intervalle -= 10

    # Uptime
    if uptime is not None and uptime < 90:
        intervalle += 20

    # Anomalies
    if nb_anomalies > 5:
        intervalle += 30
    elif nb_anomalies == 0:
        intervalle -= 10

    # Charge CPU
    if cpu_moyen > 80:
        intervalle += 20
    elif cpu_moyen < 40:
        intervalle -= 10

    # Charge RAM
    if ram_moyenne > 85:
        intervalle += 20
    elif ram_moyenne < 50:
        intervalle -= 10

    # Clamp
    intervalle = max(INTERVAL_MIN, min(INTERVAL_MAX, intervalle))

    # Logs
    log_event("INFO", f"Autoscaling → nouvel intervalle : {intervalle}s")

    # Historique
    ajouter_evenement("AUTOSCALING", "cluster", "system", f"Intervalle = {intervalle}s")

    return intervalle
