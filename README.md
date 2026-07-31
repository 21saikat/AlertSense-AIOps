# AlertSense — AI-Powered Alert Correlation & Noise Reduction Engine

AlertSense is an AIOps system that solves one of the biggest pain points in modern SRE/DevOps operations: **alert fatigue**. Instead of flooding on-call engineers with dozens of disconnected alerts during an outage, AlertSense uses Azure OpenAI to correlate related alerts into a single, enriched incident — identifying the actual root cause and the services affected as a result.

## The Problem

When a service fails in a microservices architecture, the failure cascades. A single database outage can trigger alerts from every dependent service — backend, frontend, and beyond. Engineers end up investigating 10-20 alerts that are really just symptoms of one root cause, wasting critical time during an incident.

## What AlertSense Does

- Monitors live metrics across multiple interdependent microservices
- Detects when multiple services are alerting simultaneously
- Uses Azure OpenAI + a service dependency map to identify the true root cause
- Groups related alerts into a single incident with:
  - Root cause — which service actually failed
  - Blast radius — which services are affected as a symptom
  - Suggested action — a concrete remediation step

## Architecture

frontend-service → backend-service → database-service
        ↓                 ↓                 ↓
              Prometheus (scrapes /metrics every 10s)
                          ↓
              AI Correlation Engine (Python + Azure OpenAI)
                          ↓
              Single Enriched Incident (root cause + blast radius + fix)

## Tech Stack

- Terraform — Azure VM infrastructure provisioning
- Kubernetes (kubeadm) — self-managed cluster, not a managed service, to understand cluster internals hands-on
- Docker — containerized microservices
- Prometheus — metrics collection across all services
- Azure OpenAI — root-cause reasoning and alert correlation
- Python (Flask) — microservices and correlation engine

## How It Works — Demo Walkthrough

1. Three interdependent microservices are deployed: frontend-service, backend-service, database-service
2. Each exposes a /metrics endpoint scraped by Prometheus every 10 seconds
3. When database-service is manually failed (simulating a real outage), the failure cascades:
   - database-service reports error_rate: 1.0
   - backend-service reports it can't reach the database
   - Both services fire alerts simultaneously
4. The AI correlation engine detects multiple simultaneous alerts, sends the metrics snapshot and service dependency map to Azure OpenAI, and receives back a single structured incident:

{
  "root_cause": "database-service",
  "blast_radius": ["backend-service"],
  "suggested_action": "Restore or restart database-service and verify database health and backend connectivity."
}

Instead of two disconnected alerts, the on-call engineer sees exactly what broke and what to do next.

## Project Structure

.
├── database_app.py              # Database service (Flask)
├── backend_app.py                # Backend service (Flask)
├── frontend_app.py               # Frontend service (Flask)
├── correlator.py                 # AI correlation engine
├── Dockerfile.database
├── Dockerfile.backend
├── Dockerfile.frontend
├── Dockerfile.correlator
├── requirements.txt
├── database-deployment.yaml
├── backend-deployment.yaml
├── frontend-deployment.yaml
├── correlator-deployment.yaml
├── prometheus-config.yaml
└── prometheus-deployment.yaml

## Key Learnings

- Bootstrapping Kubernetes with kubeadm (instead of a managed service like AKS) to understand cluster internals — networking, containerd configuration, control-plane taints
- Designing a service dependency map so the AI has topology context, not just raw metrics
- Structuring AI prompts to return consistent, parseable JSON for downstream automation
- Simulating cascading failures across microservices to test correlation logic under realistic conditions

## Future Improvements

- Deduplicate AI calls for ongoing incidents (avoid re-analyzing the same incident every polling cycle)
- Push incident summaries to Slack/Microsoft Teams
- Add RBAC and Kubernetes Secrets for credential management
- CI/CD pipeline with GitHub Actions for automated build and deploy

---

Built as a hands-on exploration of AIOps concepts — moving beyond static threshold-based alerting toward AI-driven incident correlation, similar to how tools like Dynatrace, PagerDuty AIOps, and Moogsoft operate at enterprise scale.
