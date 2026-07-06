import os
import json
import time
import threading
from datetime import datetime

import pandas as pd
from flask import (
    Flask,
    render_template,
    jsonify,
    Response,
    request,
    redirect,
    url_for,
    session
)

# ==========================
#   IMPORTS INTERNES
# ==========================

from db import init_db, get_conn

import hashlib
import secrets

# Monitoring / analyse
from app.history import charger_historique, charger_historique_pannes, ajouter_evenement
from history_metrics import compute_history_metrics
from app.monitor import tester_tous_les_sites
from config import FICHIER_LOG
from app.sre_module import analyser_performance_globale
from app.predictor import predire_panne
from app.comparaison import comparer_sites
from app.agents import update_agent, get_agents, ping_agents, analyser_cluster
from app.balancer import assign_sites_to_agents
from app.network import analyser_reseau
from app.agent_logs import get_agent_logs
from app.autoscaling import calculer_intervalle_optimal
from app.anomalies import detecter_anomalies, detecter_anomalie
from app.logger import log_event
from app.sites_manager import get_sites, add_site
from alerts_manager import envoyer_alertes
from app.alerts import detect_alerts
from app.autoscaling_manager import autoscaling

# ==========================
#   FLASK APP
# ==========================

app = Flask(__name__)
app.secret_key = "change_this_secret_key"

# ==========================
#   AUTH / SAAS
# ==========================

def hash_password(pwd: str) -> str:
    return hashlib.sha256(pwd.encode()).hexdigest()

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        conn = get_conn()
        c = conn.cursor()

        try:
            token = secrets.token_hex(32)
            c.execute(
                "INSERT INTO users (email, password, created_at, token) VALUES (?, ?, ?, ?)",
                (email, hash_password(password), datetime.now().isoformat(), token)
            )
            conn.commit()
        except Exception as e:
            conn.close()
            return f"Erreur inscription : {e}", 400

        conn.close()
        return redirect(url_for("login"))

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT id, password, token FROM users WHERE email = ?", (email,))
        row = c.fetchone()
        conn.close()

        if not row:
            return "Utilisateur introuvable", 400

        user_id, pwd_hash, token = row
        if hash_password(password) != pwd_hash:
            return "Mot de passe incorrect", 400

        session["user_id"] = user_id
        session["email"] = email
        session["token"] = token

        return redirect(url_for("index"))

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ==========================
#   ROUTES HTML DASHBOARD
# ==========================

@app.route("/")
def index():
    return render_template("IndexHTML.html")

@app.route("/agents")
def agents_page():
    return render_template("AgentHTML.html")

@app.route("/anomalies")
def anomalies_page():
    return render_template("AnomalieHTML.html")

@app.route("/balancing-page")
def balancing_page():
    return render_template("BalancingHTML.html")

@app.route("/comparaison")
def comparaison_page():
    return render_template("ComparaisonHTML.html")

@app.route("/config")
def config_page():
    return render_template("ConfigHTML.html")

@app.route("/graph")
def graph_page():
    return render_template("GraphHTML.html")

@app.route("/heatmap")
def heatmap_page():
    return render_template("HeatMapHTML.html")

@app.route("/historique")
def historique_page():
    return render_template("HistoriqueHTML.html")

@app.route("/categorie")
def categorie_page():
    return render_template("CatégorieHTML.html")

# ==========================
#   API OVERVIEW
# ==========================

@app.route("/api/overview")
def api_overview():
    sites = get_sites()
    agents = get_agents()

    urls = [s["url"] for s in sites]
    results = tester_tous_les_sites(urls)

    anomalies = detecter_anomalies(results)
    sre = analyser_performance_globale(results)
    network = analyser_reseau(results, agents)
    prediction = predire_panne(results)
    comparaison = comparer_sites(results)

    return jsonify({
        "sites": sites,
        "agents": agents,
        "results": results,
        "anomalies": anomalies,
        "sre": sre,
        "network": network,
        "prediction": prediction,
        "comparaison": comparaison
    })

# ==========================
#   STREAMING TEMPS RÉEL
# ==========================

@app.route("/stream")
def stream():
    def event_stream():
        while True:
            urls = [s["url"] for s in get_sites()]
            sites_results = tester_tous_les_sites(urls)
            cluster = analyser_cluster()
            anomalies = detecter_anomalies(sites_results)

            data = {
                "sites": sites_results,
                "cluster": cluster,
                "anomalies": anomalies
            }

            yield f"data: {json.dumps(data)}\n\n"
            time.sleep(5)

    return Response(event_stream(), mimetype="text/event-stream")

# ==========================
#   LOGS & HISTORIQUE
# ==========================

@app.route("/logs")
def logs_page():
    logs = []

    try:
        with open("logs.jsonl", "r") as f:
            for line in f:
                logs.append(json.loads(line))
    except FileNotFoundError:
        pass

    logs = sorted(logs, key=lambda x: x.get("timestamp", ""), reverse=True)

    return render_template("logs.html", logs=logs)

@app.route("/history")
def history_page():
    events = charger_historique()
    return render_template("history.html", events=events)

# ==========================
#   API JSON
# ==========================

@app.route("/api/status")
def api_status():
    urls = [s["url"] for s in get_sites()]
    return jsonify(tester_tous_les_sites(urls))

@app.route("/api/history")
def api_history():
    return jsonify(charger_historique_pannes())

@app.route("/api/logs")
def api_logs():
    agent = request.args.get("agent", "agent-1")
    return jsonify(get_agent_logs(agent))

# ==========================
#   API EVENTS
# ==========================

@app.route("/api/events")
def api_events():
    return jsonify(charger_historique())

# ==========================
#   API METRICS
# ==========================

@app.route("/api/metrics")
def api_metrics():
    metrics = compute_history_metrics()
    return jsonify(metrics)

# ==========================
#   AGENTS & CLUSTER
# ==========================

@app.route("/api/agent", methods=["POST"])
def api_agent():
    data = request.json
    token = data.get("token")

    if not token:
        return {"error": "missing_token"}, 400

    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE token = ?", (token,))
    row = c.fetchone()

    if not row:
        conn.close()
        return {"error": "invalid_token"}, 403

    user_id = row[0]

    name = data.get("name") or data.get("agent") or "agent"
    ip = data.get("ip", "0.0.0.0")
    version = data.get("version", "1.0")

    c.execute("""
        INSERT INTO agents (name, ip, version, owner_id, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (name, ip, version, user_id, datetime.now().isoformat()))

    conn.commit()
    conn.close()

    return {"status": "ok"}

@app.route("/cluster")
def cluster():
    if "user_id" not in session:
        return redirect(url_for("login"))

    data = analyser_cluster()
    return render_template("cluster.html", data=data)

# ==========================
#   BALANCING & RÉSEAU
# ==========================

@app.route("/balancing")
def balancing():
    df = pd.read_csv(FICHIER_LOG)
    all_sites = sorted(df["site"].unique())
    agents = get_agents()
    assignments = assign_sites_to_agents(all_sites, agents)
    return render_template("balancing.html", assignments=assignments)

@app.route("/network")
def network():
    urls = [s["url"] for s in get_sites()]
    results = tester_tous_les_sites(urls)
    agents = get_agents()
    data = analyser_reseau(results, agents)
    return render_template("network.html", data=data)

# ==========================
#   METRICS HISTORY
# ==========================

@app.route("/metrics-history")
def metrics_history():
    metrics = compute_history_metrics()
    return jsonify(metrics)

# ==========================
#   CRON MONITOR (Railway)
# ==========================

@app.route("/cron/monitor", methods=["GET"])
def cron_monitor():
    try:
        sites = [s["url"] for s in get_sites()]
        results = tester_tous_les_sites(sites)

        intervalle = calculer_intervalle_optimal(results)

        cluster_info = analyser_cluster()
        autoscaling_actions = autoscaling(cluster_info)

        history_events = charger_historique()
        alerts = detect_alerts(history_events, results, cluster_info["agents"])
        envoyer_alertes(alerts["alerts"])

        return {
            "status": "OK",
            "results": len(results),
            "alerts": len(alerts["alerts"]),
            "intervalle": intervalle["intervalle"],
            "autoscaling": autoscaling_actions["actions"]
        }

    except Exception as e:
        return {"status": "ERROR", "message": str(e)}, 500

# ==========================
#   BACKGROUND TASKS
# ==========================

def boucle_ping():
    while True:
        ping_agents()
        time.sleep(10)

threading.Thread(target=boucle_ping, daemon=True).start()

def boucle_autoscaling():
    while True:
        cluster_info = analyser_cluster()
        autoscaling(cluster_info)
        time.sleep(10)

threading.Thread(target=boucle_autoscaling, daemon=True).start()

# ==========================
#   LANCEMENT (RAILWAY)
# ==========================

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
