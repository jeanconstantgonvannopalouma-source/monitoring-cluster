import requests
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

def envoyer_alerte_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        r = requests.post(url, data=data, timeout=5)
        if r.status_code != 200:
            print(f"[TELEGRAM] Erreur {r.status_code} : {r.text}")
    except Exception as e:
        print(f"[TELEGRAM] Exception : {e}")
def envoyer_alerte_telegram_panne(site, status, latency, source):
    message = (
        f"⚠️ ALERTE SURVEILLANCE\n"
        f"Site : {site}\n"
        f"Statut : {status}\n"
        f"Latence : {latency if latency else 'N/A'} ms\n"
        f"Source : {source}\n"
        f"Dashboard : https://TON_SERVEUR/overview\n"
        f"Logs : https://TON_SERVEUR/logs\n"
    )
    envoyer_alerte_telegram(message)
