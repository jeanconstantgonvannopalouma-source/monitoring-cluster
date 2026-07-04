# autoscaling.py

def calculer_intervalle_optimal(latence_moyenne):
    """
    Retourne un intervalle simple basé sur la latence.
    """
    if latence_moyenne is None:
        return 30

    if latence_moyenne < 0.1:
        return 10
    elif latence_moyenne < 0.2:
        return 20
    else:
        return 40
