import os
import datetime
from config import FICHIER_HISTORIQUE

def enregistrer_panne(site):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(FICHIER_HISTORIQUE, "a") as f:
        f.write(f"{timestamp},{site},DOWN\n")

def charger_historique_pannes():
    if not os.path.exists(FICHIER_HISTORIQUE):
        return []

    lignes = []
    with open(FICHIER_HISTORIQUE, "r") as f:
        for ligne in f:
            timestamp, site, statut = ligne.strip().split(",")
            lignes.append({"timestamp": timestamp, "site": site, "statut": statut})
    return lignes
