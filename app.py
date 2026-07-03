from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

LOG_FILE = "logs.jsonl"

@app.route("/")
def home():
    return "Monitoring Cluster is running."

@app.route("/event", methods=["POST"])
def event():
    data = request.json
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(data) + "\n")
    return {"status": "ok"}

@app.route("/history")
def history():
    if not os.path.exists(LOG_FILE):
        return jsonify([])
    with open(LOG_FILE, "r") as f:
        lines = [json.loads(line) for line in f]
    return jsonify(lines)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
