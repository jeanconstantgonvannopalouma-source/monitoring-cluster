from datetime import datetime
from logging.logger import log_event
from logging.history import ajouter_evenement

SITES = []


def add_site(url, categorie="general", tags=None):
    """Ajoute un site avec métadonnées professionnelles."""
    if tags is None:
        tags = []

    site = {
        "url": url,
        "categorie": categorie,
        "tags": tags,
        "added_at": datetime.utcnow().isoformat(),
        "status": "UNKNOWN",
        "last_latency": None,
        "last_code": None,
        "last_agent": None,
        "anomalies": 0,
        "disponibilite": 100.0
    }

    SITES.append(site)

    log_event("INFO", f"Site ajouté : {url}", "sites_manager")
    ajouter_evenement("SITE_ADD", url, "system", f"Ajout du site ({categorie})")

    return site


def remove_site(url):
    """Supprime un site."""
    global SITES
    SITES = [s for s in SITES if s["url"] != url]

    log_event("WARNING", f"Site supprimé : {url}", "sites_manager")
    ajouter_evenement("SITE_REMOVE", url, "system", "Suppression du site")

    return True


def update_site(url, data):
    """Met à jour les métadonnées d’un site."""
    for site in SITES:
        if site["url"] == url:
            site.update(data)

            log_event("INFO", f"Site mis à jour : {url}", "sites_manager")
            ajouter_evenement("SITE_UPDATE", url, "system", str(data))

            return site
    return None


def get_sites():
    """Retourne tous les sites."""
    return SITES


def get_site(url):
    """Retourne un site spécifique."""
    for site in SITES:
        if site["url"] == url:
            return site
    return None


def get_sites_by_category(cat):
    """Retourne les sites d’une catégorie."""
    return [s for s in SITES if s["categorie"] == cat]


def get_sites_for_agent(agent_name):
    """Retourne les sites assignés à un agent."""
    return [s for s in SITES if s.get("last_agent") == agent_name]
