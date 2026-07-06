from typing import List, Dict, Any
from statistics import mean


def analyser_reseau(results: List[Dict[str, Any]], agents: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyse réseau professionnelle basée sur les résultats des tests.

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

    Retourne un rapport structuré :
    {
        "latence_moyenne": ...,
        "dns_moyen": ...,
        "sites_down": [...],
        "erreurs": [...],
        "par_agent": {
            "agent-1": {...},
            "agent-2": {...}
        }
    }
    """

    if not results:
        return {
            "latence_moyenne": None,
            "dns_moyen": None,
            "sites_down": [],
            "erreurs": [],
            "par_agent": {},
            "agents": agents
        }

    # ============================
    #   ANALYSE GLOBALE
    # ============================

    latences = [r["latency"] for r in results if r.get("latency") is not None]
    dns_times = [r["dns"] for r in results if r.get("dns") is not None]

    sites_down = [r["site"] for r in results if r.get("status") in ("ERROR", None) or (isinstance(r.get("status"), int) and r["status"] >= 500)]
    erreurs = [r for r in results if r.get("status") == "ERROR"]

    latence_moyenne = mean(latences) if latences else None
    dns_moyen = mean(dns_times) if dns_times else None

    # ============================
    #   ANALYSE PAR AGENT
    # ============================

    analyse_agents = {}

    for agent in agents:
        nom = agent.get("name", "unknown-agent")

        agent_results = [r for r in results if r.get("agent") == nom]

        if not agent_results:
            analyse_agents[nom] = {
                "tests": 0,
                "latence_moyenne": None,
                "dns_moyen": None,
                "sites_down": [],
                "erreurs": []
            }
            continue

        latences_agent = [r["latency"] for r in agent_results if r.get("latency") is not None]
        dns_agent = [r["dns"] for r in agent_results if r.get("dns") is not None]

        analyse_agents[nom] = {
            "tests": len(agent_results),
            "latence_moyenne": mean(latences_agent) if latences_agent else None,
            "dns_moyen": mean(dns_agent) if dns_agent else None,
            "sites_down": [r["site"] for r in agent_results if r.get("status") == "ERROR"],
            "erreurs": [r for r in agent_results if r.get("status") == "ERROR"]
        }

    # ============================
    #   RAPPORT FINAL
    # ============================

    rapport = {
        "latence_moyenne": latence_moyenne,
        "dns_moyen": dns_moyen,
        "sites_down": sites_down,
        "erreurs": erreurs,
        "par_agent": analyse_agents,
        "agents": agents
    }

    return rapport
