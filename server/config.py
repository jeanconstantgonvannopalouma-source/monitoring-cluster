import os

# ----------------------------------------------------------------------
# Dossiers
# ----------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

os.makedirs(DATA_DIR, exist_ok=True)

# ----------------------------------------------------------------------
# Fichiers principaux
# ----------------------------------------------------------------------

# Fichier CSV principal contenant les tests
FICHIER_LOG = os.path.join(DATA_DIR, "logs.csv")

# Fichier JSONL contenant les logs avancés
FICHIER_LOGS = os.path.join(DATA_DIR, "logs.jsonl")

# Fichier JSONL contenant l'historique des pannes
HISTORY_FILE = os.path.join(DATA_DIR, "history.jsonl")

# Fichier contenant la liste des sites
FICHIER_SITES = os.path.join(BASE_DIR, "sites.txt")

# ----------------------------------------------------------------------
# Configuration email
# ----------------------------------------------------------------------

EMAIL_FROM = "jeanconstantgonvannopalouma@gmail.com"
EMAIL_TO = "jeanconstantgonvannopalouma@gmail.com"
EMAIL_PASSWORD = "xhln kuhr ecbe xell"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# ----------------------------------------------------------------------
# Configuration Telegram
# ----------------------------------------------------------------------

TELEGRAM_TOKEN = "TON_TOKEN_ICI"
TELEGRAM_CHAT_ID = "TON_CHAT_ID_ICI"

# ----------------------------------------------------------------------
# Paramètres du monitoring
# ----------------------------------------------------------------------

MONITOR_INTERVAL = 30        # intervalle entre tests automatiques
HTTP_TIMEOUT = 5             # timeout HTTP

# ----------------------------------------------------------------------
# Seuils d'anomalies
# ----------------------------------------------------------------------

ANOMALY_LATENCY_FACTOR = 2.5
ANOMALY_VARIATION_FACTOR = 3.0

# ----------------------------------------------------------------------
# Auto-scaling
# ----------------------------------------------------------------------

INTERVAL_MIN = 10
INTERVAL_MAX = 120

# ----------------------------------------------------------------------
# Paramètres des agents
# ----------------------------------------------------------------------

AGENT_PORT = 5000

# ----------------------------------------------------------------------
# Catégorie par défaut
# ----------------------------------------------------------------------

DEFAULT_CATEGORY = "default"

# ----------------------------------------------------------------------
# Initialisation des fichiers si absents
# ----------------------------------------------------------------------

# Création du CSV principal si vide
if not os.path.exists(FICHIER_LOG):
    with open(FICHIER_LOG, "w") as f:
        f.write("timestamp,site,status,latency,source,category\n")

# Création des fichiers JSONL si absents
for fichier in [FICHIER_LOGS, HISTORY_FILE]:
    if not os.path.exists(fichier):
        with open(fichier, "w") as f:
            pass
