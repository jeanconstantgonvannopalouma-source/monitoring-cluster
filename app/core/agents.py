import time
import random

class Agent:
    def __init__(self, agent_id, name, version="1.0"):
        self.id = agent_id
        self.name = name
        self.version = version
        self.status = "ONLINE"
        self.cpu = 0
        self.ram = 0
        self.latency = None
        self.last_ping = None
        self.sites = []

    def ping(self):
        """Simule un ping de l’agent."""
        self.last_ping = time.time()

        if self.status == "ONLINE":
            self.latency = round(random.uniform(0.05, 0.30), 3)
            self.cpu = random.randint(5, 95)
            self.ram = random.randint(10, 90)
        else:
            self.latency = None
            self.cpu = None
            self.ram = None

    def assign_site(self, site):
        self.sites.append(site)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "status": self.status,
            "cpu": self.cpu,
            "ram": self.ram,
            "latency": self.latency,
            "last_ping": self.last_ping,
            "sites": self.sites
        }


# Liste des agents
AGENTS = [
    Agent(1, "agent-1"),
    Agent(2, "agent-2"),
    Agent(3, "agent-3")
]


def get_agents():
    return [a.to_dict() for a in AGENTS]


def ping_agents():
    for agent in AGENTS:
        agent.ping()
    return get_agents()


def update_agent(agent_id, status=None):
    for agent in AGENTS:
        if agent.id == agent_id:
            if status:
                agent.status = status
            return agent.to_dict()
    return None


def analyser_cluster():
    online = [a for a in AGENTS if a.status == "ONLINE"]
    offline = [a for a in AGENTS if a.status != "ONLINE"]

    latencies = [a.latency for a in online if a.latency is not None]

    return {
        "total_agents": len(AGENTS),
        "online": len(online),
        "offline": len(offline),
        "latence_moyenne": round(sum(latencies) / len(latencies), 3) if latencies else None
    }
