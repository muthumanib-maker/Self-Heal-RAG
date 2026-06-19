"""
Stage 2: Query the vector DB for incidents similar to a new alert.
"""
import json
import os

import chromadb
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
COLLECTION_NAME = "incidents"

_model = None
_client = None


def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def _get_collection():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=PERSIST_DIR)
    return _client.get_collection(COLLECTION_NAME)


def retrieve_similar_incidents(alert_text: str, n_results: int = 3):
    """
    Returns a list of dicts: {symptom, root_cause, fix_steps, risk_level,
    action_type, rollback_plan, tags, distance}
    """
    model = _get_model()
    collection = _get_collection()

    query_embedding = model.encode([alert_text]).tolist()
    results = collection.query(query_embeddings=query_embedding, n_results=n_results)

    output = []
    for i in range(len(results["ids"][0])):
        meta = results["metadatas"][0][i]
        output.append({
            "id": results["ids"][0][i],
            "symptom": results["documents"][0][i],
            "root_cause": meta.get("root_cause", ""),
            "fix_steps": json.loads(meta.get("fix_steps", "[]")),
            "risk_level": meta.get("risk_level", "unknown"),
            "action_type": meta.get("action_type", ""),
            "rollback_plan": meta.get("rollback_plan", ""),
            "tags": meta.get("tags", ""),
            "distance": results["distances"][0][i],
        })
    return output


if __name__ == "__main__":
    import sys
    query = sys.argv[1] if len(sys.argv) > 1 else "pod restarting memory error"
    for r in retrieve_similar_incidents(query):
        print(f"[{r['distance']:.3f}] {r['id']}: {r['symptom']}")
