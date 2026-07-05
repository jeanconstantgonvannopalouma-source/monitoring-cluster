import time
from datetime import datetime

# Stockage en mémoire (peut être remplacé par une DB)
LOGS = []

MAX_LOGS = 5000  # rotation automatique


def log_event(level, message, source="system"):
    """
    Ajoute un log professionnel dans la mémoire.
    - level : INFO / WARNING / ERROR
    - message : texte du log
    - source : module ou agent
    """

    log = {
        "timestamp": datetime.utcnow().isoformat(),
        "level": level,
        "source": source,
        "message": message
    }

    LOGS.append(log)

    # Rotation automatique
    if len(LOGS) > MAX_LOGS:
        del LOGS[:len(LOGS) - MAX_LOGS]

    return log


def get_logs():
    """Retourne tous les logs."""
    return LOGS
