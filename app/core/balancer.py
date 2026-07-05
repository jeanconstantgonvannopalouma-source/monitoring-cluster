from logging.logger import log_event
from logging.history import ajouter_evenement

def calculer_score(agent):
    """
    Calcule un score de charge pour un agent.
    Plus le score est élevé, plus l'agent est chargé.
    """
    cpu = agent.get("cpu") or 0
    ram = agent.get("ram") or 0
    latence = agent.get("latency") or 0
    nb_sites = len(agent.get("sites", []))

    return cpu * 0.4 + ram * 0.3 + latence * 0.2 + nb_sites * 0.1


def assign_sites_to_agents(sites, agents):
    """
    Répartition intelligente basée sur la charge des agents.
    """
    if not sites or not agents:
        return {
            "total_sites": 0,
            "total_agents": len(agents),
            "average_load": 0,
            "map": {}
        }

    # Filtrer agents offline
    agents_online = [a for a in agents if a["status"] == "ONLINE"]

    if not agents_online:
        return {
            "total_sites": len(sites),
            "total_agents": 0,
            "average_load": 0,
            "map": {}
        }

    # Calcul du score de charge
    agents_sorted = sorted(agents_online, key=lambda a: calculer_score(a))

    repartition = {a["name"]: [] for a in agents_sorted}

    # Répartition intelligente
    for site in sites:
        agent = agents_sorted[0]  # agent le moins chargé
        repartition[agent["name"]].append(site)

        # Mise à jour du score
        agent["sites"].append(site)

        # Re‑tri
        agents_sorted = sorted(agents_sorted, key=lambda a: calculer_score(a))

    # Logs
    log_event("INFO", "Répartition des sites effectuée")

    # Historique
    ajouter_evenement("BALANCING", "cluster", "system", "Répartition des sites mise à jour")

    # Calcul charge moyenne
    loads = [len(sites) for sites in repartition.values()]
    average_load = sum(loads) / len(loads)

    return {
        "total_sites": len(sites),
        "total_agents": len(agents_online),
        "average_load": round(average_load, 2),
        "map": repartition
    }
