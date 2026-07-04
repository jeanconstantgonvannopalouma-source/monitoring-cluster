# network.py

import random

def analyser_reseau():
    """Analyse réseau simple."""
    return {
        "latence_moyenne": round(random.uniform(20, 120), 2),
        "packet_loss": round(random.uniform(0, 5), 2),
        "bande_passante": round(random.uniform(50, 500), 2)
    }
