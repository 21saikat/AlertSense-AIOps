from flask import Flask, jsonify, Response
import requests
import random
import time

app = Flask(__name__)
start_time = time.time()

DATABASE_URL = "http://database-service:5000"

@app.route('/')
def home():
    return jsonify({"service": "backend-service", "status": "running"})

@app.route('/health')
def health():
    return jsonify({"status": "ok"}), 200

@app.route('/api/data')
def get_data():
    try:
        resp = requests.get(f"{DATABASE_URL}/query", timeout=2)
        if resp.status_code != 200:
            return jsonify({"error": "backend failed: database error"}), 500
        return jsonify({"backend": "ok", "data": resp.json()})
    except requests.exceptions.RequestException:
        return jsonify({"error": "backend failed: cannot reach database"}), 500

@app.route('/metrics')
def metrics():
    uptime = time.time() - start_time
    try:
        resp = requests.get(f"{DATABASE_URL}/health", timeout=2)
        db_reachable = 1 if resp.status_code == 200 else 0
    except requests.exceptions.RequestException:
        db_reachable = 0

    error_rate = 0 if db_reachable else 1.0
    cpu_sim = random.uniform(10, 30) if db_reachable else random.uniform(70, 95)

    return Response(
        f"backend_up 1\n"
        f"backend_db_reachable {db_reachable}\n"
        f"backend_error_rate {error_rate}\n"
        f"backend_cpu_simulated {cpu_sim}\n"
        f"backend_uptime_seconds {uptime}\n",
        mimetype="text/plain"
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
