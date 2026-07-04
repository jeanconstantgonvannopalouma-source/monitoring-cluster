# agents.py

import time
import random

# Stockage simple en mémoire (Railway redémarre → reset)
AGENTS = [
    {"id": 1, "name": "agent-1", "status": "online", "latence": 0.12},
    {"id": 2, "name": "agent-2", "status": "online", "latence": 0.20},
    {"id": 3, "name": "agent-3", "status": "offline", "latence": None},
]

def get_agents():
    """Retourne la liste des agents."""
    return AGENTS

def update_agent(agent_id, status=None, latence=None):
    """Met à jour un agent."""
    for agent in AGENTS:
        if agent["id"] == agent_id:
            if status is not None:
                agent["status"] = status
            if latence is not None:
                agent["latence"] = latence
            return agent
    return None

def ping_agents():
    """Simule un ping des agents."""
    for agent in AGENTS:
        if agent["status"] == "online":
            agent["latence"] = round(random.uniform(0.05, 0.30), 3)
        else:
            agent["latence"] = None
    return AGENTS

def analyser_cluster():
    """Analyse simple du cluster."""
    total = len(AGENTS)
    online = sum(1 for a in AGENTS if a["status"] == "online")
    offline = total - online

    latences = [a["latence"] for a in AGENTS if isinstance(a["latence"], float)]

    return {
        "total_agents": total,
        "online": online,
        "offline": offline,
        "latence_moyenne": round(sum(latences) / len(latences), 3) if latences else None
    }
