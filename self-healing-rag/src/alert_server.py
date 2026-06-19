"""
Stage 4: FastAPI webhook that receives alerts, runs diagnosis, and posts the
result for human review (console + optional Slack). Does NOT auto-execute
anything yet -- wire up Stage 5 (executor.py) only once you trust this.

Run with: uvicorn src.alert_server:app --reload --port 8000
"""
import os

import requests
from fastapi import FastAPI
from dotenv import load_dotenv

from diagnose import diagnose

load_dotenv()

app = FastAPI(title="Self-Healing RAG - Alert Receiver")

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")


def normalize_alert(payload: dict) -> str:
    """
    EDIT THIS to match your alerting tool's payload shape.

    Examples:
      Prometheus Alertmanager sends: payload["alerts"][0]["labels"], ["annotations"]
      Datadog sends: payload["title"], payload["body"]
      CloudWatch via SNS sends: payload["Records"][0]["Sns"]["Message"] (JSON string)

    Below is a generic fallback that just stringifies common fields.
    """
    service = payload.get("service") or payload.get("labels", {}).get("service", "unknown")
    message = (
        payload.get("message")
        or payload.get("annotations", {}).get("summary")
        or payload.get("title")
        or str(payload)
    )
    return f"{service}: {message}"


def post_to_slack(diagnosis: dict, alert_text: str):
    if not SLACK_WEBHOOK_URL:
        print("[Slack not configured] Diagnosis:", diagnosis)
        return
    text = (
        f"*New Alert:* {alert_text}\n"
        f"*Diagnosis:* {diagnosis.get('diagnosis')}\n"
        f"*Confidence:* {diagnosis.get('confidence')}\n"
        f"*Risk:* {diagnosis.get('risk_level')}\n"
        f"*Recommended action:* {diagnosis.get('recommended_action_type')}\n"
        f"*Fix steps:* {diagnosis.get('fix_steps')}\n"
        f"*Rollback:* {diagnosis.get('rollback_plan')}"
    )
    try:
        requests.post(SLACK_WEBHOOK_URL, json={"text": text}, timeout=5)
    except Exception as e:
        print(f"Failed to post to Slack: {e}")


@app.post("/alert")
async def handle_alert(payload: dict):
    alert_text = normalize_alert(payload)
    diagnosis = diagnose(alert_text)

    print("=== New Alert ===")
    print("Alert:", alert_text)
    print("Diagnosis:", diagnosis)

    post_to_slack(diagnosis, alert_text)

    # Stage 5: once you trust this, import executor.py here and call
    # maybe_auto_execute(diagnosis) for low-risk actions.

    return {"status": "diagnosed", "alert": alert_text, "diagnosis": diagnosis}


@app.get("/health")
async def health():
    return {"status": "ok"}
