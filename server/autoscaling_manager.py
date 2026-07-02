import time
from agents import get_agents, analyser_cluster, add_agent
from logger import log_event
from db import get_conn

COOLDOWN = 60  # 1 minute
last_action = 0

def autoscaling(user_id):
    global last_action

    cluster = analyser_cluster(user_id)
    cpu = cluster.get("cpu_moyen", 0)
    ram = cluster.get("ram_moyen", 0)
    agents = get_agents(user_id)
    nb_agents = len(agents)

    now = time.time()
    if now - last_action < COOLDOWN:
        return

    # ---------------------------------------------------------
    # SCALE UP (CPU ou RAM trop élevés)
    # ---------------------------------------------------------
    if cpu > 70 or ram > 80:
        log_event("autoscaling", f"Charge élevée CPU={cpu}% RAM={ram}% → ajout agent")

        result = add_agent(
            name=f"auto-agent-{int(time.time())}",
            ip="127.0.0.1",
            owner_id=user_id
        )

        if result.get("error") == "quota_reached":
            print("[AUTOSCALING] Quota atteint, impossible d'ajouter un agent.")
        else:
            print("[AUTOSCALING] Agent ajouté automatiquement.")

        last_action = now
        return

    # ---------------------------------------------------------
    # SCALE DOWN (CPU très bas)
    # ---------------------------------------------------------
    if cpu < 20 and nb_agents > 1:
        agent_to_remove = agents[-1]["name"]

        conn = get_conn()
        c = conn.cursor()
        c.execute("DELETE FROM agents WHERE name = ?", (agent_to_remove,))
        conn.commit()
        conn.close()

        log_event("autoscaling", f"Charge faible CPU={cpu}% → suppression agent {agent_to_remove}")
        print(f"[AUTOSCALING] Agent {agent_to_remove} supprimé automatiquement.")

        last_action = now
        return
