import time
import threading

from core.autoscaling import calculer_intervalle_optimal
from monitoring.monitor import tester_tous_les_sites
from core.agents import get_agents
from monitoring.anomalies import detecter_anomalies
from logging.logger import log_event
from logging.history import ajouter_evenement

# Intervalle dynamique
INTERVAL_SCAN = 30

def boucle_autoscaling():
    """Boucle d’autoscaling professionnelle."""
    global INTERVAL_SCAN

    while True:
        try:
            # Récupération des agents
            agents = get_agents()

            # Récupération des sites
            sites = [s for a in agents for s in a["sites"]]

            # Test des sites
            resultats = tester_tous_les_sites(sites)

            # Détection anomalies
            anomalies = detecter_anomalies(resultats)

            # Calcul des métriques
            latences = [r["latency"] for r in resultats if r["latency"]]
            latence_moyenne = sum(latences) / len(latences) if latences else None

            metrics = {
                "latence_moyenne": latence_moyenne,
                "dispo": 100,  # placeholder
                "uptime": 100  # placeholder
            }

            # Calcul intervalle optimal
            nouvel_intervalle = calculer_intervalle_optimal(metrics, anomalies, agents)

            # Mise à jour
            INTERVAL_SCAN = nouvel_intervalle

            # Logs
            log_event("INFO", f"Autoscaling appliqué → intervalle = {INTERVAL_SCAN}s")

            # Historique
            ajouter_evenement("AUTOSCALING", "cluster", "system", f"Intervalle = {INTERVAL_SCAN}s")

        except Exception as e:
            log_event("ERROR", f"Erreur autoscaling : {e}")

        # Attente
        time.sleep(INTERVAL_SCAN)


def lancer_autoscaling():
    """Lance le thread d’autoscaling."""
    thread = threading.Thread(target=boucle_autoscaling, daemon=True)
    thread.start()
    log_event("INFO", "Autoscaling lancé")
