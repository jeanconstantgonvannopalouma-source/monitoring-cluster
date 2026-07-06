from typing import List, Dict, Any
from statistics import mean


# ============================
#   CONFIG PREDICTION
# ============================

SEUIL_LATENCE_CRITIQUE = 2.0        # Latence > 2 sec = risque
SEUIL_DNS_CRITIQUE = 1.0            # DNS > 1 sec = risque
SEUIL_ERREURS_RECURRENTES = 3       # 3 erreurs consécutives = risque
SEUIL_VARIATION_LATENCE = 1.5       # Variation > 1.5 sec = instabilité


def _variation(values: List[float]) -> float:
    """
    Retourne la variation max-min d'une liste.
    """
    if len(values) < 2:
        return 0
    return max(values) - min(values)


def predire_panne(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Prédiction professionnelle de panne basée sur :
    - latence
    - DNS
    - erreurs
    - instabilité
    - variations
    - tendances

    Retourne :
    {
        "risque_global": ...,
        "sites_a_risque": [...],
        "details": {...}
    }
    """

    if not results:
        return {
            "risque_global": 0,
            "sites_a_risque": [],
            "details": {}
        }

    sites_risque = []
    details = {}

    # Regroupement par site
    par_site = {}
    for r in results:
        site = r["site"]
        par_site.setdefault(site, []).append(r)

    # Analyse par site
    for site, entries in par_site.items():

        latences = [e["latency"] for e in entries if e.get("latency") is not None]
        dns_times = [e["dns"] for e in entries if e.get("dns") is not None]
        erreurs = [e for e in entries if e.get("status") == "ERROR"]

        risque = 0
        motifs = []

        # 1. Latence critique
        if latences and max(latences) > SEUIL_LATENCE_CRITIQUE:
            risque += 30
            motifs.append(f"Latence critique ({max(latences)} sec)")

        # 2. DNS critique
        if dns_times and max(dns_times) > SEUIL_DNS_CRITIQUE:
            risque += 20
            motifs.append(f"DNS lent ({max(dns_times)} sec)")

        # 3. Erreurs récurrentes
        if len(erreurs) >= SEUIL_ERREURS_RECURRENTES:
            risque += 40
            motifs.append(f"{len(erreurs)} erreurs consécutives")

        # 4. Instabilité (variation latence)
        if latences and _variation(latences) > SEUIL_VARIATION_LATENCE:
            risque += 25
            motifs.append(f"Variation latence élevée ({_variation(latences)} sec)")

        # 5. Site DOWN
        if any(e.get("status") == "ERROR" for e in entries):
            risque += 15
            motifs.append("Site DOWN détecté")

        # Score final
        risque = min(risque, 100)

        details[site] = {
            "risque": risque,
            "motifs": motifs,
            "latence_moyenne": mean(latences) if latences else None,
            "dns_moyen": mean(dns_times) if dns_times else None,
            "erreurs": len(erreurs)
        }

        if risque >= 50:
            sites_risque.append(site)

    # Risque global = moyenne des risques
    risque_global = mean([d["risque"] for d in details.values()]) if details else 0

    return {
        "risque_global": round(risque_global, 2),
        "sites_a_risque": sites_risque,
        "details": details
    }
