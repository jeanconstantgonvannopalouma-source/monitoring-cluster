# agent_logs.py

LOGS = []

def get_logs():
    """Retourne les logs des agents."""
    return LOGS

def add_log(agent_id, message):
    LOGS.append({
        "agent_id": agent_id,
        "message": message
    })
