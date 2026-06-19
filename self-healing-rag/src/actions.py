"""
Stage 5: Registry of safe, pre-approved remediation actions.

CRITICAL: The LLM should only ever pick an action_type from this registry.
It should never generate raw shell/SQL/kubectl commands that get executed
directly. Each function here is something a human has reviewed and approved
in advance.

Fill in the real commands for your environment (kubectl, Ansible, AWS SSM,
etc). They are stubbed out with print statements by default so nothing runs
until you intentionally wire it up.
"""
import subprocess


def restart_pod(target: str, **kwargs):
    print(f"[ACTION] Would restart pod/deployment: {target}")
    # Example real implementation:
    # subprocess.run(["kubectl", "rollout", "restart", f"deployment/{target}"], check=True)


def scale_up(target: str, replicas: int = 5, **kwargs):
    print(f"[ACTION] Would scale {target} to {replicas} replicas")
    # subprocess.run(["kubectl", "scale", f"deployment/{target}", f"--replicas={replicas}"], check=True)


def clear_cache(target: str, **kwargs):
    print(f"[ACTION] Would clear cache for: {target}")
    # subprocess.run(["redis-cli", "-h", target, "FLUSHDB"], check=True)


def clear_disk_space(target: str, **kwargs):
    print(f"[ACTION] Would clear old logs/WAL files on: {target}")
    # subprocess.run(["ssh", target, "find /var/log -mtime +7 -delete"], check=True)


# Map action_type strings (must match what's used in your incident records
# and what the LLM is told to choose from) to the functions above.
SAFE_ACTIONS = {
    "restart_pod": restart_pod,
    "scale_up": scale_up,
    "clear_cache": clear_cache,
    "clear_disk_space": clear_disk_space,
}
