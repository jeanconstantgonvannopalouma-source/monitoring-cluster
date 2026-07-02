import json
from config import FICHIER_LOGS
import requests
import datetime
import os
from config import FICHIER_LOG, FICHIER_SITES
from alerts import envoyer_alerte
from history import enregistrer_panne
import json

with open("config.json") as f:
    CONFIG = json.load(f)

SITES = CONFIG["sites"]
CATEGORIES = CONFIG["categories"]
MONITOR_INTERVAL = CONFIG["monitoring"]["interval"]
TIMEOUT = CONFIG["monitoring"]["timeout"]
ANOMALY_LATENCY_FACTOR = CONFIG["anomalies"]["latency_factor"]
ANOMALY_VARIATION_FACTOR = CONFIG["anomalies"]["variation_factor"]

def tester_site(site):
    try:
        r = requests.get(site, timeout=5)
        return "UP" if r.status_code == 200 else "DOWN"
    except:
        return "DOWN"

def tester_tous_les_sites():
    source = "local"
f.write(f"{timestamp},{site},{status},{latency},{source}\n")
    source = "local"  # ou agent
envoyer_alerte_telegram_panne(site, status, latency, source)
    category = CATEGORIES.get(site, "Uncategorized")
f.write(f"{timestamp},{site},{status},{latency},{source},{category}\n")
for site in SITES:
    category = CATEGORIES.get(site, "Uncategorized")
    # test du site...

    if not os.path.exists(FICHIER_LOG):
        with open(FICHIER_LOG, "w") as f:
            f.write("timestamp,site,status\n")
            
    if not os.path.exists(FICHIER_LOG):
    with open(FICHIER_LOG, "w") as f:
        f.write("timestamp,site,status,latency,source,category\n")

    with open(FICHIER_SITES, "r") as f:
        sites = [s.strip() for s in f if s.strip()]

    with open(FICHIER_LOG, "a") as f:
        for site in sites:
            statut = tester_site(site)
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"{timestamp},{site},{statut}\n")

            if statut == "DOWN":
                envoyer_alerte(site)
                enregistrer_panne(site)
import time
def boucle_tests():
    while True:
        tester_tous_les_sites()
        intervalle = calculer_intervalle_optimal()
        print(f"[AUTO-SCALING] Prochain test dans {intervalle} secondes")
        time.sleep(intervalle)
def tester_site(site):
    try:
        start = time.time()
        r = requests.get(site, timeout=5)
        latency = (time.time() - start) * 1000
        status = "UP" if r.status_code == 200 else "DOWN"
    except:
        status = "DOWN"
        latency = None

    return status, latency
def generer_graphique_par_site():
    df = pd.read_csv(FICHIER_LOG)

    for site in df["site"].unique():
        df_site = df[df["site"] == site]

        fig = px.line(
            df_site,
            x="timestamp",
            y="latency",
            title=f"Latence pour {site}",
            markers=True
        )

        fig.update_layout(template="plotly_dark")
        fig.write_html(f"static/graph_{site}.html")
from telegram_alerts import envoyer_alerte_telegram

# dans la boucle, quand un site est DOWN :
if status == "DOWN":
    envoyer_alerte(site)
    enregistrer_panne(site)
    envoyer_alerte_telegram(f"⚠️ *{site}* est DOWN")
else:
    envoyer_alerte_telegram(f"🟢 *{site}* est revenu UP")
if not os.path.exists(FICHIER_LOG):
    with open(FICHIER_LOG, "w") as f:
        f.write("timestamp,site,status,latency,source\n")
def calculer_intervalle_optimal():
    df = pd.read_csv(FICHIER_LOG)

    # Si pas assez de données
    if len(df) < 10:
        return INTERVAL_MIN

    df["up"] = df["status"].eq("UP").astype(int)

    # Disponibilité récente (dernières 50 mesures)
    recent = df.tail(50)
    dispo = recent["up"].mean()

    # Latence moyenne récente
    latence = recent["latency"].dropna().mean()

    # Logique d’auto-scaling
    # Plus dispo est basse → plus on teste souvent
    # Plus latence est haute → plus on teste souvent

    score = (1 - dispo) * 0.7 + (latence / 2000) * 0.3
    score = max(0, min(score, 1))

    intervalle = INTERVAL_MIN + (INTERVAL_MAX - INTERVAL_MIN) * (1 - score)
    return int(intervalle)
def analyser_pannes():
    df = pd.read_csv(FICHIER_LOG)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["up"] = df["status"].eq("UP").astype(int)

    analyses = {}

    for site in df["site"].unique():
        df_site = df[df["site"] == site].tail(200)

        if len(df_site) < 20:
            continue

        # Instabilité = proportion de DOWN
        instabilite = 1 - df_site["up"].mean()

        # Latence moyenne
        latence_moy = df_site["latency"].dropna().mean()

        # Tendance de latence (augmentation ?)
        latences = df_site["latency"].dropna().values
        tendance = latences[-1] - latences[0] if len(latences) > 1 else 0

        # Score de risque (simple mais efficace)
        score = (
            instabilite * 0.6 +
            (latence_moy / 2000) * 0.3 +
            (tendance / 1000) * 0.1
        )

        score = max(0, min(score, 1))

        analyses[site] = {
            "instabilite": round(instabilite * 100, 2),
            "latence_moy": round(latence_moy, 2),
            "tendance": round(tendance, 2),
            "risque": round(score * 100, 2)
        }

    return analyses
def generer_rapport_sre():
    df = pd.read_csv(FICHIER_LOG)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["up"] = df["status"].eq("UP").astype(int)

    # KPIs globaux
    dispo_globale = round(df["up"].mean() * 100, 2)
    latence_moy = round(df["latency"].dropna().mean(), 2)

    # Derniers statuts
    derniers = df.sort_values("timestamp").groupby("site").tail(1)
    sites_up = derniers[derniers["status"] == "UP"]["site"].tolist()
    sites_down = derniers[derniers["status"] == "DOWN"]["site"].tolist()

    # Pannes récentes
    pannes = df[df["status"] == "DOWN"].tail(10).to_dict(orient="records")

    # Sites instables
    instabilite = (
        df.groupby("site")["up"]
          .mean()
          .mul(100)
          .round(2)
          .sort_values()
          .to_dict()
    )

    return {
        "dispo_globale": dispo_globale,
        "latence_moy": latence_moy,
        "sites_up": sites_up,
        "sites_down": sites_down,
        "pannes": pannes,
        "instabilite": instabilite
    }
def analyser_performance_globale():
    df = pd.read_csv(FICHIER_LOG)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["up"] = df["status"].eq("UP").astype(int)

    # Disponibilité globale
    dispo_globale = df["up"].mean()

    # Latence moyenne
    latence_moy = df["latency"].dropna().mean()

    # Tendance latence (sur les 100 derniers points)
    recent = df.tail(100)
    if len(recent) > 1:
        tendance_latence = recent["latency"].iloc[-1] - recent["latency"].iloc[0]
    else:
        tendance_latence = 0

    # Instabilité (proportion de DOWN)
    instabilite = 1 - dispo_globale

    # Score global (0–100)
    score = (
        dispo_globale * 0.6 +
        (1 - latence_moy / 2000) * 0.3 +
        (1 - instabilite) * 0.1
    )
    score = max(0, min(score, 1)) * 100

    return {
        "dispo_globale": round(dispo_globale * 100, 2),
        "latence_moy": round(latence_moy, 2),
        "tendance_latence": round(tendance_latence, 2),
        "instabilite": round(instabilite * 100, 2),
        "score": round(score, 2)
    }
def predire_panne(site):
    df = pd.read_csv(FICHIER_LOG)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["up"] = df["status"].eq("UP").astype(int)

    df_site = df[df["site"] == site].tail(200)

    if len(df_site) < 20:
        return {"risque": 10, "niveau": "Faible"}

    # Instabilité récente
    instabilite = 1 - df_site["up"].mean()

    # Latence moyenne
    latence_moy = df_site["latency"].dropna().mean()

    # Variance de latence
    variance = df_site["latency"].dropna().var()

    # Tendance latence
    latences = df_site["latency"].dropna().values
    tendance = latences[-1] - latences[0] if len(latences) > 1 else 0

    # Score final
    score = (
        instabilite * 0.5 +
        (latence_moy / 2000) * 0.2 +
        (variance / 50000) * 0.2 +
        (tendance / 1000) * 0.1
    )

    score = max(0, min(score, 1)) * 100

    # Niveau
    if score < 20:
        niveau = "Faible"
    elif score < 40:
        niveau = "Modéré"
    elif score < 70:
        niveau = "Élevé"
    else:
        niveau = "Critique"

    return {
        "risque": round(score, 2),
        "niveau": niveau,
        "instabilite": round(instabilite * 100, 2),
        "latence_moy": round(latence_moy, 2),
        "variance": round(variance, 2),
        "tendance": round(tendance, 2)
    }
def detecter_anomalies():
    df = pd.read_csv(FICHIER_LOG)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    anomalies = []

    for site in df["site"].unique():
        df_site = df[df["site"] == site].tail(300)

        if len(df_site) < 30:
            continue

        latences = df_site["latency"].dropna()

        if len(latences) < 10:
            continue

        moyenne = latences.mean()
        ecart_type = latences.std()

        seuil = moyenne + 2 * ecart_type

        # Détection des pics de latence
        pics = df_site[df_site["latency"] > seuil]

        for _, row in pics.iterrows():
            anomalies.append({
                "site": site,
                "type": "Pic de latence",
                "timestamp": row["timestamp"],
                "valeur": row["latency"],
                "seuil": round(seuil, 2)
            })

        # Détection des DOWN soudains
        downs = df_site[df_site["status"] == "DOWN"]
        for _, row in downs.iterrows():
            anomalies.append({
                "site": site,
                "type": "DOWN soudain",
                "timestamp": row["timestamp"],
                "valeur": None,
                "seuil": None
            })

        # Détection des variations brutales
        df_site["diff"] = df_site["latency"].diff().abs()
        variation_seuil = ANOMALY_VARIATION_FACTOR * ecart_type

        for _, row in variations.iterrows():
            anomalies.append({
                "site": site,
                "type": "Variation brutale",
                "timestamp": row["timestamp"],
                "valeur": row["diff"],
                "seuil = moyenne + ANOMALY_LATENCY_FACTOR * ecart_type"
            })

    return anomalies
def comparer_sites(sites):
    df = pd.read_csv(FICHIER_LOG)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["up"] = df["status"].eq("UP").astype(int)

    resultats = {}

    for site in sites:
        df_site = df[df["site"] == site]

        if len(df_site) == 0:
            continue

        dispo = round(df_site["up"].mean() * 100, 2)
        latence = round(df_site["latency"].dropna().mean(), 2)

        # Tendance latence
        recent = df_site.tail(100)
        if len(recent) > 1:
            tendance = recent["latency"].iloc[-1] - recent["latency"].iloc[0]
        else:
            tendance = 0

        resultats[site] = {
            "dispo": dispo,
            "latence": latence,
            "tendance": round(tendance, 2)
        }

    return resultats

