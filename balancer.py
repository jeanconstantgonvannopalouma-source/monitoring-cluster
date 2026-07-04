# balancer.py

def assign_sites_to_agents(sites, agents):
    """
    Répartition simple : round-robin.
    sites : liste d'URL
    agents : liste d'agents
    """
    if not sites or not agents:
        return {}

    repartition = {agent["id"]: [] for agent in agents}

    i = 0
    for site in sites:
        agent_id = agents[i]["id"]
        repartition[agent_id].append(site)
        i = (i + 1) % len(agents)

    return repartition
