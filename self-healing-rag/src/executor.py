"""
Stage 5: Tiered auto-execution. Low-risk, high-confidence, allow-listed
actions auto-execute. Everything else routes to a human for approval.
"""
from actions import SAFE_ACTIONS

AUTO_EXECUTE_RISK_LEVELS = {"low"}
AUTO_EXECUTE_MIN_CONFIDENCE = {"high", "medium"}


def maybe_auto_execute(diagnosis: dict, target: str, request_human_approval_fn=None):
    """
    diagnosis: dict from diagnose.py, e.g.
      {"recommended_action_type": "restart_pod", "risk_level": "low",
       "confidence": "high", ...}
    target: the service/resource name this action applies to
    request_human_approval_fn: callback to notify a human if auto-exec isn't safe
    """
    action_type = diagnosis.get("recommended_action_type")
    risk = diagnosis.get("risk_level")
    confidence = diagnosis.get("confidence")

    can_auto_execute = (
        action_type in SAFE_ACTIONS
        and risk in AUTO_EXECUTE_RISK_LEVELS
        and confidence in AUTO_EXECUTE_MIN_CONFIDENCE
    )

    if can_auto_execute:
        print(f"[AUTO-EXECUTE] action={action_type} target={target} "
              f"risk={risk} confidence={confidence}")
        SAFE_ACTIONS[action_type](target=target)
        return {"executed": True, "action": action_type, "mode": "auto"}

    print(f"[HUMAN APPROVAL REQUIRED] action={action_type} risk={risk} "
          f"confidence={confidence}")
    if request_human_approval_fn:
        request_human_approval_fn(diagnosis, target)
    return {"executed": False, "action": action_type, "mode": "manual_review"}
