from datetime import datetime
from logging.logger import log_event
from logging.history import ajouter_evenement
from alerts.telegram_alert import envoyer_telegram

# Anti-spam : mémorise les dernières alertes envoyées
DERNIERES_ALERTES = {}

def doit_envoyer(type_alerte, site):
    """Évite d'envoyer 100 fois la même alerte."""
    cle = f"{type_alerte}:{site}"
    maintenant = datetime.utcnow().timestamp()

    # Si jamais envoyée → OK
    if cle not in DERNIERES_ALERTES:
        DERNIERES_ALERTES[cle] = maintenant
        return True

    # Si envoyée il y a plus de 60 secondes → OK
    if maintenant - DERNIERES_ALERTES[cle] > 60:
        DERNIERES_ALERTES[cle] = maintenant
        return True

    # Sinon → spam
    return False


def envoyer_alerte(type_alerte, criticite, site, agent, details):
    """Envoie une alerte professionnelle."""
    if not doit_envoyer(type_alerte, site):
        return  # anti-spam

    message = f"[{criticite}] {type_alerte} sur {site} (agent: {agent}) → {details}"

    # Logs
    log_event("WARNING" if criticite == "HIGH" else "INFO", message)

    # Historique
    ajouter_evenement("ALERT", site, agent, message)

    # Telegram
    envoyer_telegram(message)

    return {
        "type": type_alerte,
        "criticite": criticite,
        "site": site,
        "agent": agent,
        "details": details,
        "timestamp": datetime.utcnow().isoformat()
    }


def alert_all(message, agents):
    """Envoie une alerte à tous les agents (version pro)."""
    ids = [a["id"] for a in agents]

    # Logs
    log_event("INFO", f"Alerte envoyée à tous les agents : {message}")

    # Historique
    ajouter_evenement("ALERT_ALL", "cluster", "system", message)

    # Telegram
    envoyer_telegram(f"[CLUSTER] {message}")

    return {
        "message": message,
        "agents_notified": ids,
        "timestamp": datetime.utcnow().isoformat()
    }
