import json
import os

# Fichier JSONL contenant l'historique des pannes
FICHIER_HISTORY = "history.jsonl"


def charger_historique():
    """
    Charge l'historique complet des pannes depuis history.jsonl.
    Retourne une liste d'événements triés du plus récent au plus ancien.
    """

    events = []

    # Si le fichier n'existe pas, on retourne une liste vide
    if not os.path.exists(FICHIER_HISTORY):
        return []

    try:
        with open(FICHIER_HISTORY, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    # Ignore les lignes corrompues
                    continue
    except Exception:
        return []

    # Tri par timestamp (du plus récent au plus ancien)
    events = sorted(events, key=lambda x: x.get("timestamp", ""), reverse=True)

    return events


def charger_historique_pannes():
    """
    Compatibilité avec ton ancien code.
    Simple alias vers charger_historique().
    """
    return charger_historique()
