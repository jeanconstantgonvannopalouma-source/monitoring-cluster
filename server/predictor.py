import pandas as pd
from config import FICHIER_LOG

def predire_panne(site):
    df = pd.read_csv(FICHIER_LOG)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["up"] = df["status"].eq("UP").astype(int)

    # Données du site (200 derniers points)
    df_site = df[df["site"] == site].tail(200)

    if len(df_site) < 20:
        return {
            "risque": 10,
            "niveau": "Faible",
            "instabilite": None,
            "latence_moy": None,
            "variance": None,
            "tendance": None
        }

    # Instabilité récente
    instabilite = 1 - df_site["up"].mean()

    # Latence moyenne
    latence_moy = df_site["latency"].dropna().mean()

    # Variance de latence
    variance = df_site["latency"].dropna().var()

    # Tendance latence (augmentation ?)
    latences = df_site["latency"].dropna().values
    tendance = latences[-1] - latences[0] if len(latences) > 1 else 0

    # Score final (0–100)
    score = (
        instabilite * 0.5 +
        (latence_moy / 2000) * 0.2 +
        (variance / 50000) * 0.2 +
        (tendance / 1000) * 0.1
    )

    score = max(0, min(score, 1)) * 100

    # Niveau de criticité
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
