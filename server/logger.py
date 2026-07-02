import json
from datetime import datetime

FICHIER_LOGS = "logs.jsonl"


def log_event(site, event, status=None, latency=None, details=None):
    """
    Log d'un événement système / monitoring / agent.

    :param site: source (site, agent, SYSTEM, etc.)
    :param event: type d'événement (ALERTE, ERREUR_EMAIL, etc.)
    :param status: statut UP/DOWN ou autre
    :param latency: latence en ms (optionnel)
    :param details: texte ou dict avec des infos supplémentaires
    """

    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "site": site,
        "event": event,
        "status": status,
        "latency": latency,
        "details": details,
    }

    try:
        with open(FICHIER_LOGS, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        # En dernier recours, on affiche dans la console
        print("Erreur log_event:", e, "| entry:", entry)
