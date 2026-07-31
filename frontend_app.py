from flask import Flask, jsonify, Response
import requests
import random
import time

app = Flask(__name__)
start_time = time.time()

BACKEND_URL = "http://backend-service:5000"

@app.route('/')
def home():
    return jsonify({"service": "frontend-service", "status": "running"})

@app.route('/health')
def health():
    return jsonify({"status": "ok"}), 200

@app.route('/api/page')
def get_page():
    try:
        resp = requests.get(f"{BACKEND_URL}/api/data", timeout=2)
        if resp.status_code != 200:
            return jsonify({"error": "frontend failed: backend error"}), 500
        return jsonify({"frontend": "ok", "page_data": resp.json()})
    except requests.exceptions.RequestException:
        return jsonify({"error": "frontend failed: cannot reach backend"}), 500

@app.route('/metrics')
def metrics():
    uptime = time.time() - start_time
    try:
        resp = requests.get(f"{BACKEND_URL}/health", timeout=2)
        backend_reachable = 1 if resp.status_code == 200 else 0
    except requests.exceptions.RequestException:
        backend_reachable = 0

    error_rate = 0 if backend_reachable else 1.0
    cpu_sim = random.uniform(10, 30) if backend_reachable else random.uniform(60, 90)

    return Response(
        f"frontend_up 1\n"
        f"frontend_backend_reachable {backend_reachable}\n"
        f"frontend_error_rate {error_rate}\n"
        f"frontend_cpu_simulated {cpu_sim}\n"
        f"frontend_uptime_seconds {uptime}\n",
        mimetype="text/plain"
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
