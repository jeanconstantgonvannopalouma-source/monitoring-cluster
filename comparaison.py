# comparaison.py

def comparer_sites(resultats):
    """
    Compare les sites testés et retourne un classement simple.
    resultats : liste de dictionnaires retournés par tester_tous_les_sites()
    """

    if not resultats:
        return {
            "classement": [],
            "nb_sites": 0
        }

    # On garde uniquement les sites qui ont une latence valide
    sites_valides = [
        r for r in resultats
        if isinstance(r.get("latence"), (int, float))
    ]

    # Tri par latence croissante (plus rapide = meilleur)
    classement = sorted(sites_valides, key=lambda x: x["latence"])

    return {
        "classement": classement,
        "nb_sites": len(resultats)
    }
