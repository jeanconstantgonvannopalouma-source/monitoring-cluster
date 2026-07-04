# alerts.py

def alert_all(message, agents):
    """Envoie une alerte simple à tous les agents."""
    return {
        "message": message,
        "agents_notified": [a["id"] for a in agents]
    }
