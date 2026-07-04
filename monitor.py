import requests
import time
from config import FICHIER_SITES, TIMEOUT

def charger_sites():
    """Charge la liste des sites à tester depuis sites.txt."""
    try:
        with open(FICHIER_SITES, "r", encoding="utf-8") as f:
            return [ligne.strip() for ligne in f.readlines() if ligne.strip()]
    except FileNotFoundError:
        return []

def tester_site(url):
    """Teste un site et retourne son statut."""
    try:
        debut = time.time()
        r = requests.get(url, timeout=TIMEOUT)
        latence = time.time() - debut

        return {
            "url": url,
            "status": r.status_code,
            "latence": latence
        }
    except Exception as e:
        return {
            "url": url,
            "status": "ERROR",
            "latence": None,
            "error": str(e)
        }

def tester_tous_les_sites():
    """Teste tous les sites et retourne les résultats."""
    sites = charger_sites()
    resultats = []

    for site in sites:
        resultats.append(tester_site(site))

    return resultats
