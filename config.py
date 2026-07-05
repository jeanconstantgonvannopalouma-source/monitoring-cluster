import os

# === Répertoire racine du projet ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# === Fichiers de données (à la racine du projet) ===
FICHIER_SITES = os.path.join(BASE_DIR, "sites.json")
FICHIER_HISTORY = os.path.join(BASE_DIR, "history.json")
FICHIER_AGENTS = os.path.join(BASE_DIR, "agents.json")

# === Fichier de logs CSV (si tu veux le garder) ===
DOSSIER_DATA = os.path.join(BASE_DIR, "data")
os.makedirs(DOSSIER_DATA, exist_ok=True)
FICHIER_LOG = os.path.join(DOSSIER_DATA, "logs.csv")

# === Email (⚠️ mot de passe DOIT être en variable d’environnement) ===
EMAIL_FROM = "jeanconstantgonvannopalouma@gmail.com"
EMAIL_TO = "jeanconstantgonvannopalouma@gmail.com"
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")  # ⚠️ sécurité
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# === Telegram ===
TELEGRAM_TOKEN = os.getenv("8844714776:AAHuMnvK4jElXI1tsqPOW1tp4rQpTlAx2oc")
TELEGRAM_CHAT_ID = os.getenv("8226897199")

# === Monitoring ===
TIMEOUT = 5
MONITOR_INTERVAL = 30  # utilisé si autoscaling désactivé

# === Seuils d'anomalies ===
ANOMALY_LATENCY_FACTOR = 2.5
ANOMALY_VARIATION_FACTOR = 3.0
ANOMALY_LATENCY_THRESHOLD = 1.0
ANOMALY_DNS_THRESHOLD = 0.5
ANOMALY_SIZE_THRESHOLD = 2_000_000
ANOMALY_UNSTABLE_THRESHOLD = 0.3

# === Auto-scaling ===
INTERVAL_MIN = 10
INTERVAL_MAX = 120

# === Flask ===
FLASK_DEBUG = True
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5000
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
