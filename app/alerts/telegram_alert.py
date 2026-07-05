import requests
from datetime import datetime
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
from logging.logger import log_event
from logging.history import ajouter_evenement

TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"


def envoyer_telegram(message, chat_id=None, parse_mode="Markdown"):
    """Envoie une alerte Telegram professionnelle avec logs + historique + retry."""
    if chat_id is None:
        chat_id = TELEGRAM_CHAT_ID

    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": parse_mode
    }

    try:
        r = requests.post(TELEGRAM_URL, data=payload, timeout=5)

        if r.status_code != 200:
            log_event("ERROR", f"[TELEGRAM] Erreur {r.status_code} : {r.text}")
            ajouter_evenement("TELEGRAM_ERROR", "cluster", "system", r.text)

            # Retry simple
            try:
                requests.post(TELEGRAM_URL, data=payload, timeout=5)
            except:
                pass

        else:
            log_event("INFO", f"[TELEGRAM] Message envoyé : {message}")
            ajouter_evenement("TELEGRAM", "cluster", "system", message)

    except Exception as e:
        log_event("ERROR", f"[TELEGRAM] Exception : {e}")
        ajouter_evenement("TELEGRAM_EXCEPTION", "cluster", "system", str(e))


def envoyer_alerte_telegram_panne(site, status, latency, source):
    """Format professionnel pour les alertes de panne."""
    message = (
        f"⚠️ *ALERTE SURVEILLANCE*\n"
        f"*Site* : {site}\n"
        f"*Statut* : {status}\n"
        f"*Latence* : {latency if latency else 'N/A'} ms\n"
        f"*Source* : {source}\n"
        f"[Dashboard](https://TON_SERVEUR/overview)\n"
        f"[Logs](https://TON_SERVEUR/logs)\n"
    )

    envoyer_telegram(message, parse_mode="Markdown")
