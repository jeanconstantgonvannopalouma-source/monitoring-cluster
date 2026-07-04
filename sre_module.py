# sre_module.py

import statistics

def analyser_performance_globale(resultats):
    """
    Analyse la performance globale des sites testés.
    resultats : liste de dictionnaires retournés par tester_tous_les_sites()
    """

    if not resultats:
        return {
            "nb_sites": 0,
            "nb_ok": 0,
            "nb_erreurs": 0,
            "latence_moyenne": None
        }

    latences = [r["latence"] for r in resultats if isinstance(r["latence"], (int, float))]
    nb_ok = sum(1 for r in resultats if r["status"] == 200)
    nb_erreurs = sum(1 for r in resultats if r["status"] != 200)

    return {
        "nb_sites": len(resultats),
        "nb_ok": nb_ok,
        "nb_erreurs": nb_erreurs,
        "latence_moyenne": statistics.mean(latences) if latences else None
    }
