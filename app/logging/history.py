import json
import os
from datetime import datetime
from config import FICHIER_HISTORY

MAX_EVENTS = 10000  # rotation automatique


def charger_historique():
    """Charge l'historique complet."""
    if not os.path.exists(FICHIER_HISTORY):
        return []

    try:
        with open(FICHIER_HISTORY, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


def sauvegarder_historique(historique):
    """Sauvegarde l'historique complet."""
    with open(FICHIER_HISTORY, "w", encoding="utf-8") as f:
        json.dump(historique, f, indent=4, ensure_ascii=False)


def ajouter_evenement(type_event, site, agent, details, criticite="INFO"):
    """Ajoute un événement professionnel dans l'historique."""
    historique = charger_historique()

    evenement = {
        "id": len(historique) + 1,
        "timestamp": datetime.utcnow().isoformat(),
        "type": type_event,
        "criticite": criticite,
        "site": site,
        "agent": agent,
        "details": details
    }

    historique.append(evenement)

    # Rotation automatique
    if len(historique) > MAX_EVENTS:
        historique = historique[-MAX_EVENTS:]

    sauvegarder_historique(historique)

    return evenement


def charger_historique_pannes():
    """Compatibilité avec ton ancien code."""
    return charger_historique()
