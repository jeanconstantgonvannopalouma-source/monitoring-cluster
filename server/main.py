import time
from tester import tester_tous_les_sites

def boucle_tests():
    while True:
        tester_tous_les_sites()
        print("[AUTO-SCALING] Prochain test dans 10 secondes")
        time.sleep(10)

if __name__ == "__main__":
    boucle_tests()
