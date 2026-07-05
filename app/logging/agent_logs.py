from datetime import datetime

# Stockage en mémoire (peut être remplacé par une DB)
AGENT_LOGS = []

MAX_AGENT_LOGS = 5000  # rotation automatique


def add_log(agent_id, level, message, source="agent"):
    """
    Ajoute un log professionnel pour un agent.
    - agent_id : identifiant de l'agent
    - level : INFO / WARNING / ERROR
    - message : texte du log
    - source : module ou agent
    """

    log = {
        "timestamp": datetime.utcnow().isoformat(),
        "agent_id": agent_id,
        "level": level,
        "source": source,
        "message": message
    }

    AGENT_LOGS.append(log)

    # Rotation automatique
    if len(AGENT_LOGS) > MAX_AGENT_LOGS:
        del AGENT_LOGS[:len(AGENT_LOGS) - MAX_AGENT_LOGS]

    return log


def get_logs(agent_id=None):
    """
    Retourne les logs des agents.
    - Si agent_id est None → retourne tous les logs.
    - Sinon → retourne uniquement les logs de cet agent.
    """
    if agent_id is None:
        return AGENT_LOGS

    return [log for log in AGENT_LOGS if log["agent_id"] == agent_id]
