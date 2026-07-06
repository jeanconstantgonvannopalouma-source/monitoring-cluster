import json
import os
from datetime import datetime

# Fichier JSONL utilisé pour stocker l'historique des événements
FICHIER_HISTORY = "history.jsonl"


def _safe_timestamp(ts: str | None = None) -> str:
    """
    Retourne un timestamp ISO 8601.
    Si ts est fourni, on le garde, sinon on génère maintenant.
    """
    if ts:
        return ts
    return datetime.utcnow().isoformat()


def ajouter_evenement(type_event: str,
                      site: str | None = None,
                      agent: str | None = None,
                      details: str | None = None,
                      timestamp: str | None = None) -> None:
    """
    Ajoute un événement dans l'historique (format JSONL).

    - type_event : "CHECK", "ERROR", "ANOMALY", etc.
    - site       : URL du site concerné (optionnel)
    - agent      : nom de l'agent (optionnel)
    - details    : message ou description (optionnel)
    - timestamp  : timestamp ISO (optionnel, sinon généré)
    """

    event = {
        "type": type_event,
        "site": site,
        "agent": agent,
        "details": details,
        "timestamp": _safe_timestamp(timestamp)
    }

    try:
        with open(FICHIER_HISTORY, "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")
    except Exception as e:
        # On ne fait pas remonter l'erreur pour ne pas casser le flux
        print(f"[history] Erreur lors de l'écriture de l'événement : {e}")


def charger_historique() -> list[dict]:
    """
    Charge l'historique complet des événements depuis history.jsonl.

    Retourne une liste de dicts triés du plus récent au plus ancien.
    Chaque événement a la forme :
    {
        "type": ...,
        "site": ...,
        "agent": ...,
        "details": ...,
        "timestamp": ...
    }
    """

    events: list[dict] = []

    if not os.path.exists(FICHIER_HISTORY):
        return []

    try:
        with open(FICHIER_HISTORY, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    ev = json.loads(line)
                    events.append(ev)
                except json.JSONDecodeError:
                    # On ignore les lignes corrompues
                    continue
    except Exception as e:
        print(f"[history] Erreur lors de la lecture de l'historique : {e}")
        return []

    # Tri du plus récent au plus ancien
    events.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

    return events


def charger_historique_pannes() -> list[dict]:
    """
    Compatibilité avec ton ancien code :
    alias vers charger_historique().

    Si tu veux un filtrage spécifique (ex : seulement type "ERROR" ou "ANOMALY"),
    tu pourras l'ajouter ici plus tard.
    """
    return charger_historique()
