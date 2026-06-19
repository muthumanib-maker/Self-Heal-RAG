"""
Quick manual test: pass an alert string, see retrieval + LLM diagnosis.

Usage:
  python scripts/test_query.py "payment-service pod keeps restarting, memory error"
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from retrieve import retrieve_similar_incidents
from diagnose import diagnose


def main():
    if len(sys.argv) < 2:
        print('Usage: python scripts/test_query.py "your alert text here"')
        return

    alert_text = sys.argv[1]

    print(f"\n=== Alert ===\n{alert_text}\n")

    print("=== Retrieved similar incidents ===")
    retrieved = retrieve_similar_incidents(alert_text)
    for r in retrieved:
        print(f"  [{r['distance']:.3f}] {r['id']}: {r['symptom']}")

    print("\n=== LLM Diagnosis ===")
    result = diagnose(alert_text)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
