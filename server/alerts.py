import requests
import smtplib
from email.mime.text import MIMEText

# ---------------------------------------------------------
# ALERTES TELEGRAM (le plus efficace)
# ---------------------------------------------------------

TELEGRAM_TOKEN = "8844714776:AAHuMnvK4jElXI1tsqPOW1tp4rQpTlAx2oc"
TELEGRAM_CHAT_ID = "8226897199"

def send_telegram_alert(message):
    """
    Envoie une alerte instantanée via Telegram.
    """
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram non configuré.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}

    try:
        requests.post(url, data=data)
        print("Alerte Telegram envoyée.")
    except Exception as e:
        print("Erreur Telegram :", e)

# ---------------------------------------------------------
# ALERTES EMAIL (second plus efficace)
# ---------------------------------------------------------

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_EMAIL = "jeanconstantgonvannopalouma@gmail.com"
SMTP_PASSWORD = "xhln kuhr ecbe xell"

def send_email_alert(to, subject, message):
    """
    Envoie une alerte email.
    """
    try:
        msg = MIMEText(message)
        msg["Subject"] = subject
        msg["From"] = SMTP_EMAIL
        msg["To"] = to

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.sendmail(SMTP_EMAIL, [to], msg.as_string())

        print("Alerte email envoyée.")
    except Exception as e:
        print("Erreur email :", e)

# ---------------------------------------------------------
# FONCTION GLOBALE D'ALERTE
# ---------------------------------------------------------

def alert_all(message, email=None):
    """
    Envoie une alerte via tous les canaux disponibles.
    """
    send_telegram_alert(message)

    if email:
        send_email_alert(email, "Alerte Monitoring", message)
