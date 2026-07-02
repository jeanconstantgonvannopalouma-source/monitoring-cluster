from agents import get_agents
from logger import log_event

def assign_sites_to_agents(all_sites):
    """
    Répartit les sites entre les agents UP en fonction de leur charge.
    Charge = CPU * 0.5 + RAM * 0.3 + nb_sites * 0.2
    """

    agents = get_agents()

    # On ne garde que les agents UP
    agents_up = {name: a for name, a in agents.items() if a["status"] == "UP"}

    if not agents_up:
        return {}  # aucun agent disponible

    # Score de charge pour chaque agent
    scores = {}
    for name, a in agents_up.items():
        cpu = a.get("cpu") or 0
        ram = a.get("ram") or 0
        nb_sites = a.get("nb_sites") or 0

        score = cpu * 0.5 + ram * 0.3 + nb_sites * 0.2
        scores[name] = score

    # Tri des agents du moins chargé au plus chargé
    agents_sorted = sorted(scores.items(), key=lambda x: x[1])

    # Répartition des sites
    assignments = {name: [] for name in agents_up.keys()}

    for i, site in enumerate(all_sites):
        agent_name = agents_sorted[i % len(agents_sorted)][0]
        assignments[agent_name].append(site)

    # Mise à jour du nombre de sites par agent
    for name, sites in assignments.items():
        agents[name]["nb_sites"] = len(sites)
        log_event(name, "Assignation sites", latency=len(sites))

    return assignments
