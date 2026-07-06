import os
from typing import Dict, Any


# ============================
#   CONFIG GÉNÉRALE
# ============================

APP_NAME = "HyperMonitor"
VERSION = "1.0.0"
ENV = os.getenv("APP_ENV", "production")  # production / development


# ============================
#   CONFIG MONITORING
# ============================

MONITOR_INTERVAL = int(os.getenv("MONITOR_INTERVAL", 30))  # secondes
TIMEOUT_REQUEST = float(os.getenv("TIMEOUT_REQUEST", 3.0))  # timeout HTTP
MAX_RETRIES = int(os.getenv("MAX_RETRIES", 2))  # retries en cas d'échec

# Seuils anomalies
SEUIL_LATENCE = float(os.getenv("SEUIL_LATENCE", 1.5))
SEUIL_DNS = float(os.getenv("SEUIL_DNS", 0.5))
SEUIL_TAILLE_MIN = int(os.getenv("SEUIL_TAILLE_MIN", 200))
SEUIL_TAILLE_MAX = int(os.getenv("SEUIL_TAILLE_MAX", 5_000_000))


# ============================
#   CONFIG SRE
# ============================

SLO_DISPONIBILITE = float(os.getenv("SLO_DISPONIBILITE", 99.9))
SLO_LATENCE_MS = float(os.getenv("SLO_LATENCE_MS", 1.0))
SLO_ERREURS = float(os.getenv("SLO_ERREURS", 0.1))


# ============================
#   CONFIG AUTOSCALING
# ============================

MAX_SITES_PER_AGENT = int(os.getenv("MAX_SITES_PER_AGENT", 10))
MIN_SITES_PER_AGENT = int(os.getenv("MIN_SITES_PER_AGENT", 2))
MAX_AGENTS = int(os.getenv("MAX_AGENTS", 20))
MIN_AGENTS = int(os.getenv("MIN_AGENTS", 1))


# ============================
#   CONFIG ALERTING
# ============================

ALERT_EMAIL = os.getenv("ALERT_EMAIL", None)
ALERT_WEBHOOK = os.getenv("ALERT_WEBHOOK", None)
ALERT_THRESHOLD_ERRORS = int(os.getenv("ALERT_THRESHOLD_ERRORS", 5))
ALERT_THRESHOLD_ANOMALIES = int(os.getenv("ALERT_THRESHOLD_ANOMALIES", 3))


# ============================
#   CONFIG FICHIERS
# ============================

HISTORY_FILE = "history.jsonl"
LOG_FILE = "logs.jsonl"
AGENTS_FILE = "agents.json"
SITES_FILE = "sites.json"
AGENT_LOGS_DIR = "agent_logs"


# ============================
#   CONFIG FLASK
# ============================

FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))
FLASK_DEBUG = ENV == "development"


# ============================
#   FONCTIONS UTILITAIRES
# ============================

def get_config() -> Dict[str, Any]:
    """Retourne toute la configuration sous forme de dict."""
    return {
        "app": {
            "name": APP_NAME,
            "version": VERSION,
            "env": ENV
        },
        "monitoring": {
            "interval": MONITOR_INTERVAL,
            "timeout": TIMEOUT_REQUEST,
            "retries": MAX_RETRIES,
            "seuils": {
                "latence": SEUIL_LATENCE,
                "dns": SEUIL_DNS,
                "taille_min": SEUIL_TAILLE_MIN,
                "taille_max": SEUIL_TAILLE_MAX
            }
        },
        "sre": {
            "slo_disponibilite": SLO_DISPONIBILITE,
            "slo_latence_ms": SLO_LATENCE_MS,
            "slo_erreurs": SLO_ERREURS
        },
        "autoscaling": {
            "max_sites_per_agent": MAX_SITES_PER_AGENT,
            "min_sites_per_agent": MIN_SITES_PER_AGENT,
            "max_agents": MAX_AGENTS,
            "min_agents": MIN_AGENTS
        },
        "alerting": {
            "email": ALERT_EMAIL,
            "webhook": ALERT_WEBHOOK,
            "threshold_errors": ALERT_THRESHOLD_ERRORS,
            "threshold_anomalies": ALERT_THRESHOLD_ANOMALIES
        },
        "files": {
            "history": HISTORY_FILE,
            "logs": LOG_FILE,
            "agents": AGENTS_FILE,
            "sites": SITES_FILE,
            "agent_logs_dir": AGENT_LOGS_DIR
        },
        "flask": {
            "host": FLASK_HOST,
            "port": FLASK_PORT,
            "debug": FLASK_DEBUG
        }
    }
