from typing import List, Dict, Any
from statistics import mean


def comparer_sites(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Comparaison professionnelle des sites monitorés.

    Chaque entrée de `results` vient de monitor.py :
    {
        "site": ...,
        "agent": ...,
        "timestamp": ...,
        "status": ...,
        "latency": ...,
        "dns": ...,
        "size": ...,
        "error": ...
    }

    Retourne :
    {
        "classement_latence": [...],
        "classement_dns": [...],
        "classement_taille": [...],
        "sites_down": [...],
        "resume": {...}
    }
    """

    if not results:
        return {
            "classement_latence": [],
            "classement_dns": [],
            "classement_taille": [],
            "sites_down": [],
            "resume": {}
        }

    # ============================
    #   FILTRAGE
    # ============================

    latences = [r for r in results if r.get("latency") is not None]
    dns_times = [r for r in results if r.get("dns") is not None]
    sizes = [r for r in results if r.get("size") is not None]

    sites_down = [
        r["site"] for r in results
        if r.get("status") == "ERROR" or (isinstance(r.get("status"), int) and r["status"] >= 500)
    ]

    # ============================
    #   CLASSEMENTS
    # ============================

    classement_latence = sorted(latences, key=lambda x: x["latency"])
    classement_dns = sorted(dns_times, key=lambda x: x["dns"])
    classement_taille = sorted(sizes, key=lambda x: x["size"], reverse=True)

    # ============================
    #   RÉSUMÉ GLOBAL
    # ============================

    resume = {
        "latence_moyenne": mean([r["latency"] for r in latences]) if latences else None,
        "dns_moyen": mean([r["dns"] for r in dns_times]) if dns_times else None,
        "taille_moyenne": mean([r["size"] for r in sizes]) if sizes else None,
        "sites_down": sites_down,
        "total_sites": len(results)
    }

    return {
        "classement_latence": classement_latence,
        "classement_dns": classement_dns,
        "classement_taille": classement_taille,
        "sites_down": sites_down,
        "resume": resume
    }
