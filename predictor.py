# predictor.py

import statistics

def predire_panne(historique):
    """
    Prédit une panne simple à partir de l'historique.
    historique : liste de dictionnaires contenant des événements passés.
    """

    if not historique:
        return {
            "prediction": "Aucune donnée",
            "risque": 0
        }

    # Exemple simple : si plus de 30% des événements sont des erreurs → risque élevé
    erreurs = sum(1 for e in historique if e.get("status") != 200)
    total = len(historique)

    risque = erreurs / total

    prediction = "Risque faible"
    if risque > 0.3:
        prediction = "Risque moyen"
    if risque > 0.6:
        prediction = "Risque élevé"

    return {
        "prediction": prediction,
        "risque": round(risque, 2)
    }
