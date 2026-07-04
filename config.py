import os

# Dossier racine du serveur
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Dossier des données
DOSSIER_DATA = os.path.join(BASE_DIR, "data")
os.makedirs(DOSSIER_DATA, exist_ok=True)

# Fichiers utilisés par le cluster
FICHIER_LOG = os.path.join(DOSSIER_DATA, "logs.csv")
FICHIER_HISTORY =os.path.join("historique_pannes.json")
FICHIER_SITES = os.path.join(BASE_DIR, "sites.txt")

# Configuration email
EMAIL_FROM = "jeanconstantgonvannopalouma@gmail.com"
EMAIL_TO = "jeanconstantgonvannopalouma@gmail.com"
EMAIL_PASSWORD = "xhln kuhr ecbe xell"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Configuration Telegram
TELEGRAM_TOKEN = "TON_TOKEN_ICI"
TELEGRAM_CHAT_ID = "TON_CHAT_ID_ICI"

# Paramètres du monitoring
MONITOR_INTERVAL = 30        # secondes
TIMEOUT = 5                  # timeout HTTP
DEBUG= True
# Seuils d'anomalies
ANOMALY_LATENCY_FACTOR = 2.5
ANOMALY_VARIATION_FACTOR = 3.0

# Auto-scaling
INTERVAL_MIN = 10
INTERVAL_MAX = 120
