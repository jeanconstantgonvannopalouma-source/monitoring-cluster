import json
import os
from datetime import datetime
from typing import Dict, Any, List

# Dossier dédié aux logs des agents
AGENT_LOGS_DIR = "agent_logs"


def _ensure_dir() -> None:
    """Crée le dossier agent_logs s'il n'existe pas."""
    if not os.path.exists(AGENT_LOGS_DIR):
        try:
            os.makedirs(AGENT_LOGS_DIR)
        except Exception as e:
            print(f"[agent_logs] Erreur création dossier : {e}")


def _get_agent_log_file(agent_name: str) -> str:
    """Retourne le chemin du fichier de log pour un agent."""
    _ensure_dir()
    safe_name = agent_name.replace(" ", "_")
    return os.path.join(AGENT_LOGS_DIR, f"{safe_name}.jsonl")


def log_agent_event(agent_name: str, level: str, message: str, extra: Dict[str, Any] | None = None) -> None:
    """
    Écrit un événement de log pour un agent spécifique.

    Exemple de ligne :
    {
        "timestamp": "...",
        "agent": "agent-1",
        "level": "INFO",
        "message": "Test OK sur https://example.com",
        "extra": {...}
    }
    """
    if extra is None:
        extra = {}

    event = {
        "timestamp": datetime.utcnow().isoformat(),
        "agent": agent_name,
        "level": level.upper(),
        "message": message,
        "extra": extra
    }

    log_file = _get_agent_log_file(agent_name)

    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")
    except Exception as e:
        print(f"[agent_logs] Erreur écriture log agent {agent_name} : {e}")


def get_agent_logs(agent_name: str, limit: int = 200) -> List[Dict[str, Any]]:
    """
    Retourne les derniers logs d'un agent.

    - limit : nombre max de lignes à retourner
    """
    log_file = _get_agent_log_file(agent_name)

    if not os.path.exists(log_file):
        return []

    events: List[Dict[str, Any]] = []

    try:
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    ev = json.loads(line)
                    events.append(ev)
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        print(f"[agent_logs] Erreur lecture logs agent {agent_name} : {e}")
        return []

    # On ne garde que les derniers `limit`
    events = events[-limit:]

    # Tri du plus récent au plus ancien
    events.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

    return events
