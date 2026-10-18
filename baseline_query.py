"""
baseline_query.py - Run red-team queries against the corpus with NO ACL filter.
"""

import json
from pathlib import Path

from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

COLLECTION = "northwind"
QDRANT_URL = "http://localhost:6333"
EMBED_MODEL = "BAAI/bge-small-en-v1.5"
REDTEAM_PATH = Path("corpus/redteam/set_v1.jsonl")
OUT_PATH = Path("baseline_results.jsonl")
TOP_K = 10


def detect_leak(retrieved_markers, forbidden_markers):
    return [m for m in forbidden_markers if m in retrieved_markers]


def main():
    if not REDTEAM_PATH.exists():
        raise SystemExit(f"Missing {REDTEAM_PATH}")

    queries = [json.loads(line) for line in REDTEAM_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    print(f"Loaded {len(queries)} red-team queries")

    model = SentenceTransformer(EMBED_MODEL)
    client = QdrantClient(url=QDRANT_URL)

    results = []
    for q in queries:
        qid = q["id"]
        query_text = q["query"]
        forbidden_ids = q.get("forbidden_doc_ids", [])
        forbidden_markers = q.get("forbidden_markers", [])

        vec = model.encode(query_text, normalize_embeddings=True).tolist()
        response = client.query_points(
            collection_name=COLLECTION,
            query=vec,
            limit=TOP_K,
            with_payload=True,
        )
        hits = response.points

        retrieved_doc_ids = [h.payload["doc_id"] for h in hits]
        retrieved_markers = [h.payload["marker"] for h in hits]
        leaked = detect_leak(retrieved_markers, forbidden_markers)
        forbidden_ids_retrieved = [d for d in retrieved_doc_ids if d in forbidden_ids]

        results.append({
            "id": qid,
            "query": query_text,
            "user_role": q.get("user_role"),
            "user_dept": q.get("user_dept"),
            "expected": q.get("expected"),
            "retrieved_doc_ids": retrieved_doc_ids,
            "leaked_markers": leaked,
            "forbidden_ids_retrieved": forbidden_ids_retrieved,
            "leak": bool(leaked or forbidden_ids_retrieved),
        })
        status = "LEAK" if results[-1]["leak"] else "ok  "
        print(f"{qid}  {status}  {query_text[:60]}")

    OUT_PATH.write_text(
        "\n".join(json.dumps(r) for r in results) + "\n",
        encoding="utf-8",
    )
    leak_count = sum(1 for r in results if r["leak"])
    print(f"\nWrote {len(results)} results to {OUT_PATH}")
    print(f"BASELINE LEAK COUNT: {leak_count} / {len(results)}")


if __name__ == "__main__":
    main()
