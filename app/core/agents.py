import json
import os
import socket
import time
from datetime import datetime
from typing import List, Dict, Any

FICHIER_AGENTS = "agents.json"

# Durée maximale avant de considérer un agent comme offline
AGENT_TIMEOUT_SEC = 30


# ============================
#   UTILITAIRES FICHIER
# ============================

def _charger_agents() -> List[Dict[str, Any]]:
    """Charge la liste des agents depuis agents.json."""
    if not os.path.exists(FICHIER_AGENTS):
        return []

    try:
        with open(FICHIER_AGENTS, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _sauvegarder_agents(agents: List[Dict[str, Any]]) -> None:
    """Sauvegarde la liste des agents dans agents.json."""
    try:
        with open(FICHIER_AGENTS, "w", encoding="utf-8") as f:
            json.dump(agents, f, indent=4)
    except Exception as e:
        print(f"[agents] Erreur sauvegarde agents : {e}")


# ============================
#   API PUBLIQUE
# ============================

def get_agents() -> List[Dict[str, Any]]:
    """Retourne la liste des agents."""
    return _charger_agents()


def update_agent(name: str, ip: str, version: str) -> Dict[str, Any]:
    """
    Ajoute ou met à jour un agent.
    - name : nom de l'agent
    - ip : adresse IP
    - version : version de l'agent
    """

    agents = _charger_agents()

    # Vérifie si l'agent existe déjà
    for agent in agents:
        if agent["name"] == name:
            agent["ip"] = ip
            agent["version"] = version
            agent["last_seen"] = datetime.utcnow().isoformat()
            _sauvegarder_agents(agents)
            return agent

    # Sinon, nouvel agent
    nouveau = {
        "name": name,
        "ip": ip,
        "version": version,
        "created_at": datetime.utcnow().isoformat(),
        "last_seen": datetime.utcnow().isoformat(),
        "status": "ONLINE"
    }

    agents.append(nouveau)
    _sauvegarder_agents(agents)
    return nouveau


def _ping(ip: str, timeout: float = 1.0) -> bool:
    """
    Ping réseau simple via socket.
    Retourne True si l'IP répond, False sinon.
    """

    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((ip, 80))
        return True
    except Exception:
        return False


def ping_agents() -> None:
    """
    Met à jour le statut ONLINE / OFFLINE des agents.
    Un agent est OFFLINE si :
    - son IP ne répond pas
    - OU son last_seen dépasse AGENT_TIMEOUT_SEC
    """

    agents = _charger_agents()
    now = time.time()

    for agent in agents:
        ip = agent.get("ip", "0.0.0.0")
        last_seen = agent.get("last_seen")

        # Vérifie le ping réseau
        online = _ping(ip)

        # Vérifie le timeout last_seen
        if last_seen:
            delta = now - datetime.fromisoformat(last_seen).timestamp()
            if delta > AGENT_TIMEOUT_SEC:
                online = False

        agent["status"] = "ONLINE" if online else "OFFLINE"

    _sauvegarder_agents(agents)


def analyser_cluster() -> Dict[str, Any]:
    """
    Analyse professionnelle du cluster d'agents.

    Retourne :
    {
        "total_agents": ...,
        "online": ...,
        "offline": ...,
        "agents": [...],
        "stats": {
            "online_rate": ...,
            "offline_rate": ...
        }
    }
    """

    agents = _charger_agents()

    total = len(agents)
    online = sum(1 for a in agents if a.get("status") == "ONLINE")
    offline = total - online

    online_rate = round((online / total * 100), 2) if total else 0
    offline_rate = round((offline / total * 100), 2) if total else 0

    return {
        "total_agents": total,
        "online": online,
        "offline": offline,
        "agents": agents,
        "stats": {
            "online_rate": online_rate,
            "offline_rate": offline_rate
        }
    }
