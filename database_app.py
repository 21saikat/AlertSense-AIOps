from flask import Flask, jsonify, Response
import random
import time

app = Flask(__name__)
start_time = time.time()

# এই flag-টা দিয়ে আমরা ইচ্ছাকৃতভাবে সার্ভিস "down" সিমুলেট করবো
IS_HEALTHY = True

@app.route('/')
def home():
    return jsonify({"service": "database-service", "status": "running"})

@app.route('/health')
def health():
    if IS_HEALTHY:
        return jsonify({"status": "ok"}), 200
    else:
        return jsonify({"status": "down"}), 500

@app.route('/query')
def query():
    if not IS_HEALTHY:
        return jsonify({"error": "database connection failed"}), 500
    time.sleep(random.uniform(0.05, 0.2))
    return jsonify({"result": "sample_data", "rows": 42})

@app.route('/metrics')
def metrics():
    uptime = time.time() - start_time
    error_rate = 0 if IS_HEALTHY else 1.0
    cpu_sim = random.uniform(10, 30) if IS_HEALTHY else random.uniform(80, 99)
    return Response(
        f"db_up {1 if IS_HEALTHY else 0}\n"
        f"db_error_rate {error_rate}\n"
        f"db_cpu_simulated {cpu_sim}\n"
        f"db_uptime_seconds {uptime}\n",
        mimetype="text/plain"
    )

@app.route('/toggle-failure', methods=['POST'])
def toggle_failure():
    global IS_HEALTHY
    IS_HEALTHY = not IS_HEALTHY
    return jsonify({"is_healthy": IS_HEALTHY})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
