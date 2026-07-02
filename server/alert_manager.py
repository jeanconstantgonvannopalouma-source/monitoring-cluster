import smtplib
from email.mime.text import MIMEText
from logger import log_event

# -----------------------------
# CONFIG EMAIL (GMAIL)
# -----------------------------
EMAIL_FROM = "jeanconstantgonvannopalouma@gmail.com"
EMAIL_TO = "jeanconstantgonvannopalouma@gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587


def envoyer_email(sujet, message):
    """
    Envoie une alerte email via Gmail + log l'événement.
    """
    try:
        msg = MIMEText(message, "plain", "utf-8")
        msg["Subject"] = sujet
        msg["From"] = EMAIL_FROM
        msg["To"] = EMAIL_TO

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()

            # -----------------------------
            # ICI tu mets ton mot de passe d'application Gmail
            # -----------------------------
            server.login(
                EMAIL_FROM,
                "xhln kuhr ecbe xell"
            )

            server.send_message(msg)

        # Log succès
        log_event(
            site="SYSTEM",
            event="Alerte email envoyée",
            details={"subject": sujet, "message": message},
        )

    except Exception as e:
        # Log erreur
        log_event(
            site="SYSTEM",
            event="Erreur email",
            details=str(e),
        )


def alerte(source, titre, details):
    """
    Déclenche une alerte :
    - log
    - email
    """
    # Log de l’alerte
    log_event(
        site=source,
        event=titre,
        details=details,
    )

    # Envoi email
    sujet = f"[ALERTE] {titre} - {source}"
    msg = f"Source : {source}\n\nDétails : {details}"
    envoyer_email(sujet, msg)
