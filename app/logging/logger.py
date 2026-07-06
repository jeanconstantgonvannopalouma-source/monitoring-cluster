import json
import os
from datetime import datetime

# Fichier principal des logs
LOG_FILE = "logs.jsonl"

# Taille maximale avant rotation (en octets)
MAX_LOG_SIZE = 5 * 1024 * 1024   # 5 MB


def _rotate_logs():
    """
    Rotation automatique des logs :
    - Si logs.jsonl dépasse MAX_LOG_SIZE → on renomme en logs_YYYYMMDD_HHMMSS.jsonl
    - Nouveau fichier logs.jsonl créé automatiquement
    """
    if not os.path.exists(LOG_FILE):
        return

    if os.path.getsize(LOG_FILE) < MAX_LOG_SIZE:
        return

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    new_name = f"logs_{timestamp}.jsonl"

    try:
        os.rename(LOG_FILE, new_name)
        print(f"[logger] Rotation des logs → {new_name}")
    except Exception as e:
        print(f"[logger] Erreur rotation logs : {e}")


def log_event(level: str, message: str, agent: str | None = None, site: str | None = None):
    """
    Log professionnel en JSONL.

    Exemple de ligne :
    {
        "timestamp": "...",
        "level": "INFO",
        "message": "Test OK",
        "agent": "agent-1",
        "site": "https://example.com"
    }

    - level : "INFO", "WARNING", "ERROR"
    - message : texte du log
    - agent : nom de l’agent (optionnel)
    - site : URL du site concerné (optionnel)
    """

    event = {
        "timestamp": datetime.utcnow().isoformat(),
        "level": level.upper(),
        "message": message,
        "agent": agent,
        "site": site
    }

    # Rotation si nécessaire
    _rotate_logs()

    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")
    except Exception as e:
        print(f"[logger] Erreur écriture log : {e}")
