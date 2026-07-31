import time
import urllib.request
import json
from openai import AzureOpenAI

# ================================
# আপনার Azure OpenAI ডিটেইলস এখানে বসান
# ================================
AZURE_ENDPOINT = "https://projdau.openai.azure.com"
AZURE_API_KEY = "Azure kay paste here"
DEPLOYMENT_NAME = "it"
# ================================

SERVICES = {
    "database-service": "http://database-service:5000/metrics",
    "backend-service": "http://backend-service:5000/metrics",
    "frontend-service": "http://frontend-service:5000/metrics",
}

# Dependency map: কে কার উপর নির্ভরশীল (topology knowledge)
DEPENDENCY_MAP = {
    "frontend-service": ["backend-service"],
    "backend-service": ["database-service"],
    "database-service": [],
}

client = AzureOpenAI(
    azure_endpoint=AZURE_ENDPOINT,
    api_key=AZURE_API_KEY,
    api_version="2024-02-15-preview"
)

def fetch_metrics(url):
    try:
        raw = urllib.request.urlopen(url, timeout=3).read().decode()
        metrics = {}
        for line in raw.strip().split("\n"):
            key, value = line.split(" ")
            metrics[key] = float(value)
        return metrics
    except Exception as e:
        return {"error": str(e)}

def collect_all_metrics():
    snapshot = {}
    for name, url in SERVICES.items():
        snapshot[name] = fetch_metrics(url)
    return snapshot

def detect_anomalies(snapshot):
    """কোন সার্ভিসগুলোর error_rate > 0, সেগুলোকে 'firing alert' হিসেবে ধরি"""
    alerts = []
    for service, metrics in snapshot.items():
        error_key = [k for k in metrics if "error_rate" in k]
        if error_key and metrics[error_key[0]] > 0:
            alerts.append(service)
    return alerts

def ask_ai_for_root_cause(alerts, snapshot):
    prompt = f"""
You are an SRE AIOps assistant. Multiple services fired alerts simultaneously.

Alerting services: {alerts}
Service dependency map (service -> depends on): {json.dumps(DEPENDENCY_MAP)}
Full metrics snapshot: {json.dumps(snapshot, indent=2)}

Based on the dependency map and metrics, identify:
1. The single root cause service (the one that isn't dependent on anything else that's also failing)
2. The blast radius (which services are affected as a symptom)
3. A one-line suggested remediation action

Respond ONLY in this exact JSON format, no extra text:
{{"root_cause": "...", "blast_radius": [...], "suggested_action": "..."}}
"""
    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[{"role": "user", "content": prompt}],
        max_completion_tokens=200
    )
    return response.choices[0].message.content.strip()

def main_loop():
    print("[AlertSense] Correlation engine started. Watching services...")
    while True:
        snapshot = collect_all_metrics()
        alerts = detect_anomalies(snapshot)

        if len(alerts) == 0:
            print("[OK] All services healthy. No alerts.")
        elif len(alerts) == 1:
            print(f"[SINGLE ALERT] {alerts[0]} — no correlation needed.")
        else:
            print(f"[RAW ALERTS] {len(alerts)} alerts fired: {alerts}")
            print("[AI] Correlating alerts into a single incident...")
            result = ask_ai_for_root_cause(alerts, snapshot)
            print("=" * 50)
            print("[INCIDENT SUMMARY]")
            print(result)
            print("=" * 50)

        time.sleep(15)

if __name__ == "__main__":
    main_loop()
