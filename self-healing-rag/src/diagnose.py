"""
Stage 3: Diagnose a new alert using retrieved past incidents + Claude.
"""
import json
import os

import anthropic
from dotenv import load_dotenv

from retrieve import retrieve_similar_incidents

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

DIAGNOSIS_PROMPT = """You are an SRE assistant performing automated incident triage.

Given a new alert and similar past incidents (with their root causes and fixes),
diagnose the likely cause and recommend a fix.

New Alert:
{alert_text}

Similar Past Incidents:
{context}

Respond with ONLY valid JSON, no other text, in this exact shape:
{{
  "diagnosis": "string - likely root cause",
  "confidence": "high | medium | low",
  "recommended_action_type": "string - should match an action_type from past incidents if applicable, else 'unknown'",
  "fix_steps": ["step 1", "step 2"],
  "risk_level": "low | medium | high",
  "rollback_plan": "string"
}}"""


def format_context(retrieved):
    if not retrieved:
        return "No similar past incidents found."
    parts = []
    for r in retrieved:
        parts.append(
            f"- Symptom: {r['symptom']}\n"
            f"  Root cause: {r['root_cause']}\n"
            f"  Fix steps: {r['fix_steps']}\n"
            f"  Risk level: {r['risk_level']}\n"
            f"  Action type: {r['action_type']}\n"
            f"  Rollback: {r['rollback_plan']}"
        )
    return "\n\n".join(parts)


def diagnose(alert_text: str, n_results: int = 3) -> dict:
    retrieved = retrieve_similar_incidents(alert_text, n_results=n_results)
    context = format_context(retrieved)

    prompt = DIAGNOSIS_PROMPT.format(alert_text=alert_text, context=context)

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )

    raw_text = response.content[0].text.strip()
    raw_text = raw_text.replace("```json", "").replace("```", "").strip()

    try:
        diagnosis = json.loads(raw_text)
    except json.JSONDecodeError:
        diagnosis = {
            "diagnosis": "PARSE_ERROR",
            "confidence": "low",
            "recommended_action_type": "unknown",
            "fix_steps": [],
            "risk_level": "high",
            "rollback_plan": "",
            "raw_response": raw_text,
        }

    diagnosis["retrieved_incidents"] = [r["id"] for r in retrieved]
    return diagnosis


if __name__ == "__main__":
    import sys
    alert = sys.argv[1] if len(sys.argv) > 1 else "payment-service pod restarting, memory error"
    result = diagnose(alert)
    print(json.dumps(result, indent=2))
