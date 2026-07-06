from typing import List, Dict, Any


def assign_sites_to_agents(sites: List[str], agents: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """
    Répartition professionnelle des sites entre les agents.

    - sites : liste des URLs
    - agents : liste des agents (dicts venant de agents.py)

    Retourne :
    {
        "agent-1": ["site1", "site2"],
        "agent-2": ["site3"],
        ...
    }

    Algorithme :
    - Round-robin équilibré
    - Si aucun agent → retourne {}
    - Si un seul agent → tous les sites lui sont assignés
    """

    assignments: Dict[str, List[str]] = {}

    if not agents:
        return {}

    # Normalisation des noms d'agents
    agent_names = [a.get("name", "agent-unknown") for a in agents]

    # Initialisation
    for name in agent_names:
        assignments[name] = []

    # Round-robin professionnel
    index = 0
    total_agents = len(agent_names)

    for site in sites:
        agent_name = agent_names[index]
        assignments[agent_name].append(site)

        index = (index + 1) % total_agents

    return assignments


def compute_agent_load(assignments: Dict[str, List[str]]) -> Dict[str, int]:
    """
    Retourne la charge de chaque agent (nombre de sites assignés).

    Exemple :
    {
        "agent-1": 5,
        "agent-2": 3
    }
    """
    return {agent: len(sites) for agent, sites in assignments.items()}


def find_overloaded_agents(assignments: Dict[str, List[str]], threshold: int = 10) -> List[str]:
    """
    Détecte les agents surchargés.

    - threshold : nombre max de sites avant surcharge

    Retourne une liste des agents surchargés.
    """
    overloaded = []
    for agent, sites in assignments.items():
        if len(sites) > threshold:
            overloaded.append(agent)
    return overloaded


def rebalance(assignments: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """
    Rééquilibrage professionnel des sites entre agents.

    - Récupère tous les sites
    - Répartit à nouveau via round-robin

    Retourne un nouvel assignments équilibré.
    """
    all_sites = []
    agents = list(assignments.keys())

    for sites in assignments.values():
        all_sites.extend(sites)

    return assign_sites_to_agents(all_sites, [{"name": a} for a in agents])
