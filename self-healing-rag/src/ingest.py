"""
Stage 1-2: Load incident records from data/incidents/*.json into a
persistent Chroma vector DB collection.

Run this any time you add/update incident records.
"""
import json
import os
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

INCIDENTS_DIR = Path(__file__).parent.parent / "data" / "incidents"
PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
COLLECTION_NAME = "incidents"


def load_incidents():
    incidents = []
    for f in INCIDENTS_DIR.glob("*.json"):
        if f.name.startswith("_"):  # skip templates
            continue
        with open(f) as fh:
            incidents.append(json.load(fh))
    return incidents


def main():
    print("Loading embedding model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    client = chromadb.PersistentClient(path=PERSIST_DIR)

    # Recreate collection fresh each run (simple approach for a starter kit)
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = client.create_collection(COLLECTION_NAME)

    incidents = load_incidents()
    if not incidents:
        print(f"No incident files found in {INCIDENTS_DIR}. Add some JSON "
              f"records (see _TEMPLATE.json) before running this.")
        return

    print(f"Embedding and indexing {len(incidents)} incidents...")
    documents = [inc["symptom"] for inc in incidents]
    embeddings = model.encode(documents).tolist()
    ids = [inc["id"] for inc in incidents]
    metadatas = [
        {
            "root_cause": inc.get("root_cause", ""),
            "fix_steps": json.dumps(inc.get("fix_steps", [])),
            "risk_level": inc.get("risk_level", "unknown"),
            "action_type": inc.get("action_type", ""),
            "rollback_plan": inc.get("rollback_plan", ""),
            "tags": ",".join(inc.get("tags", [])),
        }
        for inc in incidents
    ]

    collection.add(
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids,
    )

    print(f"Done. Indexed {len(incidents)} incidents into '{COLLECTION_NAME}' "
          f"at {PERSIST_DIR}")


if __name__ == "__main__":
    main()
