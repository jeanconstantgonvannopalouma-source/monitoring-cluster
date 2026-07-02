import pandas as pd
from config import FICHIER_LOG

def comparer_sites(sites):
    df = pd.read_csv(FICHIER_LOG)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["up"] = df["status"].eq("UP").astype(int)

    resultats = {}

    for site in sites:
        df_site = df[df["site"] == site]

        if len(df_site) == 0:
            resultats[site] = {
                "dispo": None,
                "latence": None,
                "tendance": None
            }
            continue

        # Disponibilité
        dispo = round(df_site["up"].mean() * 100, 2)

        # Latence moyenne
        latence = round(df_site["latency"].dropna().mean(), 2)

        # Tendance latence (100 derniers points)
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
