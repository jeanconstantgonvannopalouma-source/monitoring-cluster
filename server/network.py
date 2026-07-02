import time
import requests
from agents import get_agents
from logger import log_event
from alert_manager import alerte
from history import ajouter_evenement


def analyser_reseau():
    """
    Analyse la connectivité entre agents.
    Retourne :
    - latence entre agents
    - liens UP/DOWN
    - topologie simple
    """

    agents = get_agents()
    resultat = {
        "nodes": [],
        "links": []
    }

    # Ajouter les agents comme noeuds
    for name, a in agents.items():
        resultat["nodes"].append({
            "id": name,
            "ip": a["ip"],
            "status": a["status"],
            "cpu": a.get("cpu"),
            "ram": a.get("ram"),
            "uptime": a.get("uptime"),
            "nb_sites": a.get("nb_sites")
        })

    # Tester la connectivité entre agents
    noms = list(agents.keys())

    for i in range(len(noms)):
        for j in range(i + 1, len(noms)):
            a1 = agents[noms[i]]
            a2 = agents[noms[j]]

            ip1 = a1["ip"]
            ip2 = a2["ip"]

            url = f"http://{ip1}:5000/ping-agent?target={ip2}"

            try:
                t0 = time.time()
                r = requests.get(url, timeout=2)
                latency = round((time.time() - t0) * 1000, 2)

                if r.status_code == 200:
                    resultat["links"].append({
                        "source": noms[i],
                        "target": noms[j],
                        "status": "UP",
                        "latency": latency
                    })

                    # Log réseau OK
                    log_event(
                        f"{noms[i]}->{noms[j]}",
                        "Lien UP",
                        latency=latency
                    )

                else:
                    resultat["links"].append({
                        "source": noms[i],
                        "target": noms[j],
                        "status": "DOWN",
                        "latency": None
                    })

                    # Alerte lien DOWN
                    alerte(
                        f"{noms[i]}->{noms[j]}",
                        "Lien réseau DOWN",
                        f"Impossible de joindre {ip2}"
                    )

                    ajouter_evenement(
                        f"{noms[i]}->{noms[j]}",
                        "NETWORK_DOWN",
                        f"Ping non valide vers {ip2}"
                    )

            except Exception as e:
                resultat["links"].append({
                    "source": noms[i],
                    "target": noms[j],
                    "status": "DOWN",
                    "latency": None
                })

                # Alerte lien DOWN
                alerte(
                    f"{noms[i]}->{noms[j]}",
                    "Lien réseau DOWN",
                    str(e)
                )

                ajouter_evenement(
                    f"{noms[i]}->{noms[j]}",
                    "NETWORK_DOWN",
                    str(e)
                )

    return resultat
