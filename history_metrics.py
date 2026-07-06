import json
import os
from datetime import datetime
from typing import Dict, Any, List

HISTORY_FILE = "history.jsonl"


def _load_history() -> List[Dict[str, Any]]:
    """Charge l'historique complet depuis history.jsonl."""
    if not os.path.exists(HISTORY_FILE):
        return []

    events = []

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    ev = json.loads(line)
                    events.append(ev)
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        print(f"[history_metrics] Erreur lecture historique : {e}")
        return []

    return events


def _parse_timestamp(ts: str) -> datetime | None:
    """Convertit un timestamp ISO en datetime."""
    try:
        return datetime.fromisoformat(ts.replace("Z", ""))
    except Exception:
        return None


def compute_history_metrics() -> Dict[str, Any]:
    """
    Analyse professionnelle de l'historique des événements.

    Retourne :
    {
        "total_events": ...,
        "checks": ...,
        "errors": ...,
        "anomalies": ...,
        "per_agent": {...},
        "per_site": {...},
        "timeline": [...],
        "first_event": ...,
        "last_event": ...
    }
    """

    events = _load_history()

    if not events:
        return {
            "total_events": 0,
            "checks": 0,
            "errors": 0,
            "anomalies": 0,
            "per_agent": {},
            "per_site": {},
            "timeline": [],
            "first_event": None,
            "last_event": None
        }

    total_events = len(events)
    checks = sum(1 for e in events if e.get("type") == "CHECK")
    errors = sum(1 for e in events if e.get("type") == "ERROR")
    anomalies = sum(1 for e in events if e.get("type") == "ANOMALY")

    # ============================
    #   PAR AGENT
    # ============================

    per_agent: Dict[str, Dict[str, int]] = {}

    for e in events:
        agent = e.get("agent", "unknown")
        per_agent.setdefault(agent, {"checks": 0, "errors": 0, "anomalies": 0})

        if e.get("type") == "CHECK":
            per_agent[agent]["checks"] += 1
        elif e.get("type") == "ERROR":
            per_agent[agent]["errors"] += 1
        elif e.get("type") == "ANOMALY":
            per_agent[agent]["anomalies"] += 1

    # ============================
    #   PAR SITE
    # ============================

    per_site: Dict[str, Dict[str, int]] = {}

    for e in events:
        site = e.get("site", "unknown")
        per_site.setdefault(site, {"checks": 0, "errors": 0, "anomalies": 0})

        if e.get("type") == "CHECK":
            per_site[site]["checks"] += 1
        elif e.get("type") == "ERROR":
            per_site[site]["errors"] += 1
        elif e.get("type") == "ANOMALY":
            per_site[site]["anomalies"] += 1

    # ============================
    #   TIMELINE
    # ============================

    timeline = []

    for e in events:
        ts = _parse_timestamp(e.get("timestamp", ""))
        if ts:
            timeline.append({"timestamp": ts.isoformat(), "type": e.get("type")})

    timeline.sort(key=lambda x: x["timestamp"])

    first_event = timeline[0]["timestamp"] if timeline else None
    last_event = timeline[-1]["timestamp"] if timeline else None

    # ============================
    #   RAPPORT FINAL
    # ============================

    return {
        "total_events": total_events,
        "checks": checks,
        "errors": errors,
        "anomalies": anomalies,
        "per_agent": per_agent,
        "per_site": per_site,
        "timeline": timeline,
        "first_event": first_event,
        "last_event": last_event
    }
