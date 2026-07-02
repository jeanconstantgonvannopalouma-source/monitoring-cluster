from db import get_conn
from datetime import datetime

# ---------------------------------------------------------
# QUOTAS SELON LE PLAN STRIPE
# ---------------------------------------------------------

def get_max_agents(plan):
    quotas = {
        "starter": 1,
        "pro": 5,
        "business": 20,
        "enterprise": 9999
    }
    return quotas.get(plan, 1)

# ---------------------------------------------------------
# RÉCUPÉRER LES AGENTS D'UN USER
# ---------------------------------------------------------

def get_agents(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT name, ip, version, created_at FROM agents WHERE owner_id = ?", (user_id,))
    rows = c.fetchall()
    conn.close()

    agents = []
    for r in rows:
        agents.append({
            "name": r[0],
            "ip": r[1],
            "version": r[2],
            "created_at": r[3]
        })
    return agents

# ---------------------------------------------------------
# AJOUTER UN AGENT (utilisé par autoscaling + API)
# ---------------------------------------------------------

def add_agent(name, ip, owner_id, version="1.0"):
    conn = get_conn()
    c = conn.cursor()

    # Vérifier le quota Stripe
    c.execute("SELECT plan FROM users WHERE id = ?", (owner_id,))
    row = c.fetchone()
    plan = row[0] if row else "starter"

    current_agents = len(get_agents(owner_id))
    max_agents = get_max_agents(plan)

    if current_agents >= max_agents:
        conn.close()
        return {"error": "quota_reached", "max": max_agents}

    c.execute("""
        INSERT INTO agents (name, ip, version, owner_id, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (name, ip, version, owner_id, datetime.now().isoformat()))

    conn.commit()
    conn.close()

    return {"status": "ok", "agent": name}

# ---------------------------------------------------------
# METTRE À JOUR UN AGENT
# ---------------------------------------------------------

def update_agent(name, ip):
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        UPDATE agents SET ip = ?, updated_at = ?
        WHERE name = ?
    """, (ip, datetime.now().isoformat(), name))

    conn.commit()
    conn.close()

# ---------------------------------------------------------
# PING DES AGENTS
# ---------------------------------------------------------

def ping_agents():
    # Ici tu peux ajouter un vrai ping réseau si tu veux
    pass

# ---------------------------------------------------------
# ANALYSE DU CLUSTER
# ---------------------------------------------------------

def analyser_cluster(user_id):
    """
    Retourne un résumé du cluster :
    - nombre d'agents
    - CPU moyenne
    - RAM moyenne
    - état global
    """
    try:
        with open("agent_metrics.jsonl", "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        return {"cpu_moyen": 0, "ram_moyen": 0, "agents": 0}

    cpu_values = []
    ram_values = []

    for line in lines:
        try:
            data = json.loads(line)
            if data.get("owner_id") == user_id:
                cpu_values.append(data.get("cpu", 0))
                ram_values.append(data.get("ram", 0))
        except:
            pass

    cpu_moyen = sum(cpu_values) / len(cpu_values) if cpu_values else 0
    ram_moyen = sum(ram_values) / len(ram_values) if ram_values else 0

    return {
        "cpu_moyen": cpu_moyen,
        "ram_moyen": ram_moyen,
        "agents": len(get_agents(user_id))
    }
