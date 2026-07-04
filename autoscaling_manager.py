# autoscaling_manager.py

def autoscaling(cluster_info):
    """
    Autoscaling simple basé sur le nombre d'agents offline.
    """
    if cluster_info["offline"] > 1:
        return "Augmenter les agents"
    return "Stable"
