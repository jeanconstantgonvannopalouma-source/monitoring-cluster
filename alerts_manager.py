import json
import requests
import smtplib
from email.mime.text import MIMEText
from typing import Dict, Any, List

from config import ALERT_EMAIL, ALERT_WEBHOOK
from history import ajouter_evenement
from logger import log


# ============================
#   ENVOI PAR EMAIL
# ============================

def _send_email(subject: str, body: str) -> bool:
    """
    Envoi d'une alerte par email.
    Utilise ALERT_EMAIL dans config.py.
    """

    if not ALERT_EMAIL:
        return False

    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = "hypermonitor@system"
        msg["To"] = ALERT_EMAIL

        # SMTP local ou service externe (Railway)
        with smtplib.SMTP("localhost") as server:
            server.sendmail(msg["From"], [msg["To"]], msg.as_string())

        return True

    except Exception as e:
        log("ERROR", f"[alerts_manager] Erreur envoi email : {e}")
        return False


# ============================
#   ENVOI PAR WEBHOOK
# ============================

def _send_webhook(payload: Dict[str, Any]) -> bool:
    """
    Envoi d'une alerte via webhook HTTP.
    Utilise ALERT_WEBHOOK dans config.py.
    """

    if not ALERT_WEBHOOK:
        return False

    try:
        r = requests.post(ALERT_WEBHOOK, json=payload, timeout=3)
        return r.status_code in (200, 201, 204)

    except Exception as e:
        log("ERROR", f"[alerts_manager] Erreur webhook : {e}")
        return False


# ============================
#   ENVOI D'UNE ALERTE
# ============================

def envoyer_alerte(alert: Dict[str, Any]) -> Dict[str, Any]:
    """
    Envoie une alerte via :
    - email
    - webhook
    - console (fallback)
    - historique

    Retourne :
    {
        "sent_email": True/False,
        "sent_webhook": True/False,
        "stored": True/False
    }
    """

    sujet = f"[ALERTE] {alert.get('type')}"
    message = alert.get("message", "Alerte sans message")

    # Email
    sent_email = _send_email(sujet, message)

    # Webhook
    sent_webhook = _send_webhook(alert)

    # Console fallback
    if not sent_email and not sent_webhook:
        print(f"[ALERTE] {alert}")

    # Historique
    try:
        ajouter_evenement("ALERT", alert.get("site"), alert.get("agent"), alert.get("type"))
        stored = True
    except Exception as e:
        log("ERROR", f"[alerts_manager] Erreur stockage alerte : {e}")
        stored = False

    return {
        "sent_email": sent_email,
        "sent_webhook": sent_webhook,
        "stored": stored
    }


# ============================
#   ENVOI D'UNE LISTE D'ALERTES
# ============================

def envoyer_alertes(alerts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Envoie une liste d'alertes.
    Retourne les résultats individuels.
    """

    results = []

    for alert in alerts:
        res = envoyer_alerte(alert)
        results.append({
            "alert": alert,
            "result": res
        })

    return results
