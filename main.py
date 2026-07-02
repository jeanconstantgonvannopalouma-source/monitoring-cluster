if __name__ == "__main__":
    boucle_tests()
    def boucle_tests():
    while True:
        tester_tous_les_sites()
        intervalle = calculer_intervalle_optimal()
        print(f"[AUTO-SCALING] Prochain test dans {intervalle} secondes")
        time.sleep(intervalle)

