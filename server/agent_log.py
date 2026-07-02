import json
import time
import os

# Fichier de logs persistants
FICHIER_AGENT_LOGS = "data/agent_logs.jsonl"

# Logs en mémoire (pour vitesse)
LOGS = []

# On limite à 500 logs en mémoire
MAX_LOGS = 500


def log_event(agent, event, details=None, status=None, latency=None):
    """
    Enregistre un événement d'agent dans :
    - un fichier JSONL (persistant)
    - une liste en mémoire (rapide)
    """

    entry = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "agent": agent,
        "event": event,
        "details": details,
        "status": status,
        "latency": latency
    }

    # Ajout en mémoire
    LOGS.append(entry)
    if len(LOGS) > MAX_LOGS:
        LOGS.pop(0)

    # Création du dossier si nécessaire
    dossier = os.path.dirname(FICHIER_AGENT_LOGS)
    os.makedirs(dossier, exist_ok=True)

    # Ajout dans le fichier JSONL
    with open(FICHIER_AGENT_LOGS, "a") as f:
        f.write(json.dumps(entry) + "\n")

    return entry


def get_logs():
    """
    Retourne les 500 derniers logs (mémoire + fichier si nécessaire)
    """

    # Si la mémoire contient déjà les logs → rapide
    if LOGS:
        return LOGS[-MAX_LOGS:]

    # Sinon on recharge depuis le fichier
    entries = []
    if os.path.exists(FICHIER_AGENT_LOGS):
        with open(FICHIER_AGENT_LOGS, "r") as f:
            for line in f:
                try:
                    entries.append(json.loads(line))
                except:
                    pass

    return entries[-MAX_LOGS:]
