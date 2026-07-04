# alerts_manager.py

ALERTS = []

def add_alert(message):
    ALERTS.append(message)
    return True

def get_alerts():
    return ALERTS
