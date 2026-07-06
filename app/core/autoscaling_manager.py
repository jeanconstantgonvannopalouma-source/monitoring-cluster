from typing import Dict, Any, List
from balancer import assign_sites_to_agents, compute_agent_load, find_overloaded_agents, rebalance
from agents import get_agents, update_agent


# ============================
#   CONFIG AUTOSCALING
# ============================

MAX_SITES_PER_AGENT = 10          # seuil de surcharge
MIN_SITES_PER_AGENT = 2           # seuil de sous-utilisation
MAX_AGENTS = 20                   # limite cluster
MIN_AGENTS = 1                    # minimum cluster


def autoscaling(cluster_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Autoscaling professionnel basé sur :
    - nombre d'agents
    - charge par agent
    - surcharge
    - sous-utilisation
    - rééquilibrage automatique

    cluster_info vient de analyser_cluster() :
    {
        "total_agents": ...,
        "online": ...,
        "offline": ...,
        "agents": [...],
        "stats": {...}
    }
    """

    agents = cluster_info.get("agents", [])
    total_agents = cluster_info.get("total_agents", 0)

    # Si aucun agent → autoscaling impossible
    if total_agents == 0:
        return {
            "action": "NO_AGENTS",
            "details": "Aucun agent disponible pour autoscaling."
        }

    # ============================
    #   CHARGES DES AGENTS
    # ============================

    # On récupère les sites assignés via balancer
    sites = []
    for agent in agents:
        sites.extend(agent.get("sites", []))  # si tu veux stocker les sites dans agents.json

    assignments = assign_sites_to_agents(sites, agents)
    load = compute_agent_load(assignments)

    overloaded = find_overloaded_agents(assignments, threshold=MAX_SITES_PER_AGENT)
    underloaded = [a for a, count in load.items() if count < MIN_SITES_PER_AGENT]

    actions = []

    # ============================
    #   SCALE UP (ajout d'agents)
    # ============================

    if overloaded and total_agents < MAX_AGENTS:
        new_agent_name = f"agent-auto-{total_agents + 1}"
        update_agent(new_agent_name, "127.0.0.1", "1.0")

        actions.append({
            "action": "SCALE_UP",
            "agent_added": new_agent_name,
            "reason": f"Agents surchargés : {overloaded}"
        })

        # Rééquilibrage après ajout
        assignments = rebalance(assignments)

    # ============================
    #   SCALE DOWN (suppression d'agents)
    # ============================

    if underloaded and total_agents > MIN_AGENTS:
        # On retire le premier agent sous-utilisé
        agent_to_remove = underloaded[0]

        actions.append({
            "action": "SCALE_DOWN",
            "agent_removed": agent_to_remove,
            "reason": f"Agent sous-utilisé ({load[agent_to_remove]} sites)"
        })

        # On ne supprime pas physiquement l'agent du fichier ici,
        # mais tu peux ajouter une fonction remove_agent() si tu veux.

        # Rééquilibrage après suppression
        assignments = rebalance(assignments)

    # ============================
    #   RÉÉQUILIBRAGE SIMPLE
    # ============================

    if not overloaded and not underloaded:
        actions.append({
            "action": "REBALANCE",
            "details": "Rééquilibrage automatique du cluster."
        })
        assignments = rebalance(assignments)

    # ============================
    #   RAPPORT FINAL
    # ============================

    return {
        "actions": actions,
        "assignments": assignments,
        "load": load,
        "overloaded": overloaded,
        "underloaded": underloaded,
        "total_agents": total_agents
    }
