import pandas as pd
from config import FICHIER_LOG

def generer_rapport_sre():
    df = pd.read_csv(FICHIER_LOG)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["up"] = df["status"].eq("UP").astype(int)

    # Disponibilité globale
    dispo_globale = round(df["up"].mean() * 100, 2)

    # Latence moyenne
    latence_moy = round(df["latency"].dropna().mean(), 2)

    # Derniers statuts par site
    derniers = df.sort_values("timestamp").groupby("site").tail(1)
    sites_up = derniers[derniers["status"] == "UP"]["site"].tolist()
    sites_down = derniers[derniers["status"] == "DOWN"]["site"].tolist()

    # Pannes récentes
    pannes = df[df["status"] == "DOWN"].tail(10).to_dict(orient="records")

    # Instabilité par site
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

    # Tendance latence (100 derniers points)
    recent = df.tail(100)
    if len(recent) > 1:
        tendance_latence = recent["latency"].iloc[-1] - recent["latency"].iloc[0]
    else:
        tendance_latence = 0

    # Instabilité
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
