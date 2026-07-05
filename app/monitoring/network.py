from logging.logger import log_event
from logging.history import ajouter_evenement

def analyser_reseau(resultats, agents):
    """
    Analyse réseau professionnelle basée sur les résultats du monitor.
    - latence moyenne
    - sites lents
    - agents en surcharge réseau
    - matrice réseau pour heatmap
    """

    # Latence moyenne
    latences = [r["latency"] for r in resultats if r["latency"]]
    latence_moyenne = round(sum(latences) / len(latences), 3) if latences else None

    # Sites lents
    sites_lents = [r["site"] for r in resultats if r["latency"] and r["latency"] > 1.0]

    # Agents en surcharge réseau
    agents_surcharge = []
    for agent in agents:
        agent_latences = [
            r["latency"] for r in resultats if r["agent"] == agent["name"] and r["latency"]
        ]
        if agent_latences:
            moyenne = sum(agent_latences) / len(agent_latences)
            if moyenne > 0.8:
                agents_surcharge.append(agent["name"])

    # Matrice réseau (agents → sites → latence)
    matrix = []
    for agent in agents:
        lignes = []
        for r in resultats:
            if r["agent"] == agent["name"]:
                lignes.append({
                    "site": r["site"],
                    "value": r["latency"] or 0
                })

        matrix.append({
            "agent": agent["name"],
            "latences": lignes
        })

    # Logs
    log_event("INFO", "Analyse réseau effectuée")

    # Historique
    ajouter_evenement("NETWORK", "cluster", "system", "Analyse réseau mise à jour")

    return {
        "latence_moyenne": latence_moyenne,
        "agents_surcharge": agents_surcharge,
        "sites_lents": sites_lents,
        "agents": agents,
        "matrix": matrix
    }
