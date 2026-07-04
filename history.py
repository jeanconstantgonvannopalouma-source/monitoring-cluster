# history.py

import json
import os
from config import FICHIER_HISTORIQUE

def charger_historique_pannes():
    """Charge l'historique des pannes depuis le fichier JSON."""
    if not os.path.exists(FICHIER_HISTORIQUE):
        return []

    with open(FICHIER_HISTORIQUE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def sauvegarder_historique_pannes(historique):
    """Sauvegarde l'historique des pannes dans le fichier JSON."""
    with open(FICHIER_HISTORIQUE, "w", encoding="utf-8") as f:
        json.dump(historique, f, indent=4, ensure_ascii=False)
