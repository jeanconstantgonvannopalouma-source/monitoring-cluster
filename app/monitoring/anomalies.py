from typing import Optional, Dict

# Seuils professionnels (tu peux les ajuster)
SEUIL_LATENCE_MS = 1.5      # 1.5 secondes
SEUIL_TAILLE_MIN = 200      # 200 bytes
SEUIL_TAILLE_MAX = 5_000_000  # 5 MB
SEUIL_DNS = 0.5             # 0.5 secondes


def detecter_anomalie(result: Dict) -> Optional[Dict]:
    """
    Détection professionnelle d'anomalies sur un test de site.

    Le dict `result` vient de monitor.py :
    {
        "site": ...,
        "agent": ...,
        "timestamp": ...,
        "status": ...,
        "latency": ...,
        "dns": ...,
        "size": ...,
        "error": ...
    }

    Retourne :
    {
        "type": "LATENCY_HIGH",
        "details": "Latence 2.3 sec"
    }

    Ou None si aucune anomalie.
    """

    # 1. Erreur réseau / HTTP
    if result.get("status") == "ERROR":
        return {
            "type": "NETWORK_ERROR",
            "details": result.get("error", "Erreur inconnue")
        }

    # 2. Code HTTP anormal
    status = result.get("status")
    if isinstance(status, int) and status >= 500:
        return {
            "type": "HTTP_5XX",
            "details": f"Code HTTP {status}"
        }

    # 3. Latence élevée
    latence = result.get("latency")
    if latence is not None and latence > SEUIL_LATENCE_MS:
        return {
            "type": "LATENCY_HIGH",
            "details": f"Latence {latence} sec"
        }

    # 4. DNS lent
    dns = result.get("dns")
    if dns is not None and dns > SEUIL_DNS:
        return {
            "type": "DNS_SLOW",
            "details": f"DNS {dns} sec"
        }

    # 5. Taille de réponse anormale
    size = result.get("size")
    if size is not None:
        if size < SEUIL_TAILLE_MIN:
            return {
                "type": "RESPONSE_TOO_SMALL",
                "details": f"Taille {size} bytes"
            }
        if size > SEUIL_TAILLE_MAX:
            return {
                "type": "RESPONSE_TOO_LARGE",
                "details": f"Taille {size} bytes"
            }

    # 6. Site DOWN (status non 200)
    if isinstance(status, int) and status not in (200, 201, 204):
        return {
            "type": "SITE_DOWN",
            "details": f"Status {status}"
        }

    # Aucune anomalie
    return None
