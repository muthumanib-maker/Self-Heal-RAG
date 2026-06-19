"""
Stage 6: After a fix (auto or human-approved) is applied and verified, log
the outcome as a new incident record so the knowledge base grows. Re-run
ingest.py afterwards (or on a schedule) to re-index.
"""
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

INCIDENTS_DIR = Path(__file__).parent.parent / "data" / "incidents"


def log_outcome(symptom: str, root_cause: str, fix_steps: list,
                 risk_level: str, action_type: str, rollback_plan: str,
                 outcome: str, tags: list = None):
    """
    outcome: 'resolved', 'failed', or 'recurred'
    """
    record = {
        "id": f"INC-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6]}",
        "symptom": symptom,
        "root_cause": root_cause,
        "fix_steps": fix_steps,
        "risk_level": risk_level,
        "action_type": action_type,
        "rollback_plan": rollback_plan,
        "outcome": outcome,
        "tags": tags or [],
        "logged_at": datetime.now(timezone.utc).isoformat(),
    }

    out_path = INCIDENTS_DIR / f"{record['id']}.json"
    with open(out_path, "w") as f:
        json.dump(record, f, indent=2)

    print(f"Logged new incident record: {out_path}")
    print("Remember to re-run `python src/ingest.py` to re-index.")
    return record


if __name__ == "__main__":
    # Example usage
    log_outcome(
        symptom="checkout-service 502 errors during flash sale",
        root_cause="Insufficient replicas for traffic spike",
        fix_steps=["Scaled checkout-service from 3 to 10 replicas"],
        risk_level="low",
        action_type="scale_up",
        rollback_plan="kubectl scale deployment/checkout-service --replicas=3",
        outcome="resolved",
        tags=["scaling", "checkout-service"],
    )
