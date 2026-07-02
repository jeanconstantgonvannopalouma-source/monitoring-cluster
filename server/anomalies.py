import statistics
import pandas as pd
from datetime import datetime

from config import FICHIER_LOG
from logger import log_event
from alert_manager import alerte
from history import ajouter_evenement


class AnomalyDetector:
    """
    Détecteur d'anomalies en live (temps réel).
    Analyse :
    - temps de réponse
    - statuts UP/DOWN
    - spikes soudains
    """

    def __init__(self):
        self.response_history = {}  # {site: [latences]}
        self.status_history = {}    # {site: [(status, timestamp)]}
        self.anomalies = []         # liste interne
        self.threshold_response_ms = 1500
        self.threshold_spike_factor = 2.5
        self.max_history = 20

    def add_response_time(self, site, response_time_ms):
        if site not in self.response_history:
            self.response_history[site] = []

        self.response_history[site].append(response_time_ms)

        if len(self.response_history[site]) > self.max_history:
            self.response_history[site].pop(0)

        self.detect_response_anomaly(site)

    def add_status(self, site, status):
        if site not in self.status_history:
            self.status_history[site] = []

        self.status_history[site].append((status, datetime.now()))

        if len(self.status_history[site]) > self.max_history:
            self.status_history[site].pop(0)

        self.detect_status_anomaly(site)

    def detect_response_anomaly(self, site):
        history = self.response_history.get(site, [])
        if len(history) < 5:
            return

        latest = history[-1]
        avg = statistics.mean(history[:-1])

        # Anomalie 1 : temps de réponse trop élevé
        if latest > self.threshold_response_ms:
            self._register_anomaly(site, "Réponse trop lente", f"{latest} ms")
            alerte(site, "Latence élevée", f"{latest} ms")

        # Anomalie 2 : spike soudain
        if avg > 0 and latest > avg * self.threshold_spike_factor:
            self._register_anomaly(
                site,
                "Spike de latence",
                f"{latest} ms (moyenne {int(avg)} ms)"
            )
            alerte(site, "Spike de latence", f"{latest} ms (moyenne {int(avg)} ms)")

    def detect_status_anomaly(self, site):
        history = self.status_history.get(site, [])
        if len(history) < 2:
            return

        last_status, _ = history[-1]
        prev_status, _ = history[-2]

        # Anomalie : changement soudain UP → DOWN
        if prev_status == "UP" and last_status == "DOWN":
            self._register_anomaly(site, "Site tombé", "DOWN")
            alerte(site, "Site tombé", "DOWN")

        # Anomalie : changement soudain DOWN → UP
        if prev_status == "DOWN" and last_status == "UP":
            self._register_anomaly(site, "Site revenu UP", "UP")
            alerte(site, "Site revenu UP", "UP")

    def _register_anomaly(self, site, anomaly_type, value):
        anomaly = {
            "site": site,
            "type": anomaly_type,
            "value": value,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.anomalies.append(anomaly)

        # Log dans logs.jsonl
        log_event(site, anomaly_type, details=value)

        # Historique
        ajouter_evenement(site, anomaly_type, value)

    def get_anomalies(self):
        return self.anomalies

    def get_latest_anomalies(self, limit=10):
        return self.anomalies[-limit:]


# ----------------------------------------------------------------------
# Analyse des anomalies dans le CSV (historique)
# ----------------------------------------------------------------------

def detecter_anomalies():
    """
    Analyse les anomalies dans le fichier CSV :
    - sites instables
    - latence moyenne élevée
    - spikes
    - sites souvent DOWN
    """

    df = pd.read_csv(FICHIER_LOG)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["up"] = df["status"].eq("UP").astype(int)

    anomalies = []

    # Sites instables
    instabilite = (
        df.groupby("site")["up"]
          .mean()
          .mul(100)
          .round(2)
          .sort_values()
    )

    for site, dispo in instabilite.items():
        if dispo < 80:
            anomalies.append({
                "site": site,
                "type": "Instabilité",
                "value": f"Disponibilité {dispo}%",
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            alerte(site, "Instabilité", f"Disponibilité {dispo}%")

    # Latence moyenne élevée
    latences = (
        df.groupby("site")["latency"]
          .mean()
          .round(2)
          .sort_values(ascending=False)
    )

    for site, lat in latences.items():
        if lat > 1500:
            anomalies.append({
                "site": site,
                "type": "Latence élevée",
                "value": f"{lat} ms",
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            alerte(site, "Latence élevée", f"{lat} ms")

    # Sites souvent DOWN
    down_counts = (
        df[df["status"] == "DOWN"]
        .groupby("site")
        .size()
        .sort_values(ascending=False)
    )

    for site, count in down_counts.items():
        if count >= 3:
            anomalies.append({
                "site": site,
                "type": "Pannes fréquentes",
                "value": f"{count} DOWN",
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            alerte(site, "Pannes fréquentes", f"{count} DOWN")

    return anomalies
