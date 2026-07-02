import json
import os
from datetime import datetime, timedelta

# Fichier JSONL pour l'historique des pannes
HISTORY_FILE = "data/history.jsonl"

# Cache mémoire pour accélérer les lectures
HISTORY_CACHE = []
MAX_CACHE = 500


def _ensure_directory():
    """Crée le dossier data/ si nécessaire."""
    dossier = os.path.dirname(HISTORY_FILE)
    os.makedirs(dossier, exist_ok=True)


def ajouter_evenement(site, type_evenement, details=""):
    """
    Ajoute un événement dans l'historique des pannes.
    Format JSONL : une ligne = un événement.
    """

    _ensure_directory()

    evenement = {
        "site": site,
        "type": type_evenement,
        "details": details,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Ajout dans le cache mémoire
    HISTORY_CACHE.append(evenement)
    if len(HISTORY_CACHE) > MAX_CACHE:
        HISTORY_CACHE.pop(0)

    # Ajout dans le fichier JSONL
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(evenement) + "\n")

    return evenement


def charger_historique_pannes():
    """
    Charge l'historique complet depuis le fichier JSONL.
    Utilisé par /historique et /api/history.
    """

    if HISTORY_CACHE:
        return HISTORY_CACHE[-MAX_CACHE:]

    if not os.path.exists(HISTORY_FILE):
        return []

    events = []
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                events.append(json.loads(line))
            except:
                pass

    HISTORY_CACHE.extend(events[-MAX_CACHE:])
    return events


def get_derniers_evenements(limit=20):
    """
    Retourne les derniers événements.
    """

    events = charger_historique_pannes()
    return events[-limit:]


def get_evenements_site(site, limit=50):
    """
    Retourne les événements d'un site spécifique.
    """

    events = charger_historique_pannes()
    filtres = [e for e in events if e["site"] == site]
    return filtres[-limit:]


def get_evenements_24h():
    """
    Retourne les événements des dernières 24 heures.
    """

    events = charger_historique_pannes()
    seuil = datetime.now() - timedelta(hours=24)

    return [
        e for e in events
        if datetime.strptime(e["timestamp"], "%Y-%m-%d %H:%M:%S") >= seuil
    ]


def get_evenements_7j():
    """
    Retourne les événements des 7 derniers jours.
    """

    events = charger_historique_pannes()
    seuil = datetime.now() - timedelta(days=7)

    return [
        e for e in events
        if datetime.strptime(e["timestamp"], "%Y-%m-%d %H:%M:%S") >= seuil
    ]
