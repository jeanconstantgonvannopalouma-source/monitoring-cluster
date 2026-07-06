import json
import os
from datetime import datetime
from typing import List, Dict, Any

FICHIER_SITES = "sites.json"


# ============================
#   UTILITAIRES FICHIER
# ============================

def _charger_sites() -> List[Dict[str, Any]]:
    """Charge la liste des sites depuis sites.json."""
    if not os.path.exists(FICHIER_SITES):
        return []

    try:
        with open(FICHIER_SITES, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _sauvegarder_sites(sites: List[Dict[str, Any]]) -> None:
    """Sauvegarde la liste des sites dans sites.json."""
    try:
        with open(FICHIER_SITES, "w", encoding="utf-8") as f:
            json.dump(sites, f, indent=4)
    except Exception as e:
        print(f"[sites_manager] Erreur sauvegarde sites : {e}")


# ============================
#   API PUBLIQUE
# ============================

def get_sites() -> List[Dict[str, Any]]:
    """Retourne la liste des sites."""
    return _charger_sites()


def add_site(url: str,
             categorie: str = "general",
             tags: List[str] | None = None) -> Dict[str, Any]:
    """
    Ajoute un site professionnel dans la base.

    - url : URL du site
    - categorie : catégorie (ex: ecommerce, api, blog)
    - tags : liste de tags (optionnel)

    Retourne le site ajouté ou une erreur.
    """

    if tags is None:
        tags = []

    sites = _charger_sites()

    # Vérifie si le site existe déjà
    for s in sites:
        if s["url"] == url:
            return {"error": "Site déjà existant"}

    nouveau = {
        "url": url,
        "categorie": categorie,
        "tags": tags,
        "added_at": datetime.utcnow().isoformat(),

        # Métadonnées professionnelles
        "status": "UNKNOWN",
        "last_check": None,
        "last_latency": None,
        "last_dns": None,
        "last_code": None,
        "last_agent": None,

        # SRE metrics
        "uptime": 100.0,
        "disponibilite": 100.0,
        "anomalies": 0,
        "checks_total": 0,
        "checks_ok": 0,
        "checks_error": 0
    }

    sites.append(nouveau)
    _sauvegarder_sites(sites)

    return nouveau


def update_site_metrics(url: str, result: Dict[str, Any]) -> None:
    """
    Met à jour les métriques d'un site après un test.
    Utilisé par monitor.py ou par les agents.
    """

    sites = _charger_sites()

    for s in sites:
        if s["url"] == url:

            s["last_check"] = result.get("timestamp")
            s["last_latency"] = result.get("latency")
            s["last_dns"] = result.get("dns")
            s["last_code"] = result.get("status")
            s["last_agent"] = result.get("agent")

            # SRE metrics
            s["checks_total"] += 1

            if isinstance(result.get("status"), int) and result["status"] < 500:
                s["checks_ok"] += 1
            else:
                s["checks_error"] += 1
                s["anomalies"] += 1

            # Disponibilité
            if s["checks_total"] > 0:
                s["disponibilite"] = round((s["checks_ok"] / s["checks_total"]) * 100, 2)

            break

    _sauvegarder_sites(sites)


def delete_site(url: str) -> bool:
    """
    Supprime un site de la base.
    Retourne True si supprimé, False sinon.
    """

    sites = _charger_sites()
    new_sites = [s for s in sites if s["url"] != url]

    if len(new_sites) == len(sites):
        return False

    _sauvegarder_sites(new_sites)
    return True
