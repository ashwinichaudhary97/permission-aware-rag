"""
benign_query.py - Run benign queries through baseline and filtered; measure pass rate.
"""

import json
from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.models import FieldCondition, Filter, MatchAny
from sentence_transformers import SentenceTransformer

COLLECTION = "northwind"
QDRANT_URL = "http://localhost:6333"
EMBED_MODEL = "BAAI/bge-small-en-v1.5"
BENIGN_PATH = Path("corpus/benign/set_v1.jsonl")
OUT_PATH = Path("benign_results.jsonl")
TOP_K = 10


def build_acl_filter(user_role: str, user_dept: str) -> Filter:
    return Filter(
        must=[
            FieldCondition(key="allowed_roles", match=MatchAny(any=[user_role])),
            FieldCondition(key="allowed_depts", match=MatchAny(any=[user_dept])),
        ]
    )


def main():
    queries = [json.loads(line) for line in BENIGN_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    print(f"Loaded {len(queries)} benign queries")

    model = SentenceTransformer(EMBED_MODEL)
    client = QdrantClient(url=QDRANT_URL)

    results = []
    for q in queries:
        qid = q["id"]
        query_text = q["query"]
        user_role = q["user_role"]
        user_dept = q["user_dept"]

        vec = model.encode(query_text, normalize_embeddings=True).tolist()

        # Baseline: no filter
        base_hits = client.query_points(
            collection_name=COLLECTION,
            query=vec,
            limit=TOP_K,
            with_payload=True,
        ).points

        # Filtered: role+dept ACL
        filt_hits = client.query_points(
            collection_name=COLLECTION,
            query=vec,
            query_filter=build_acl_filter(user_role, user_dept),
            limit=TOP_K,
            with_payload=True,
        ).points

        rec = {
            "id": qid,
            "query": query_text,
            "user_role": user_role,
            "user_dept": user_dept,
            "baseline_hits": len(base_hits),
            "filtered_hits": len(filt_hits),
            "baseline_top_doc": base_hits[0].payload["doc_id"] if base_hits else None,
            "filtered_top_doc": filt_hits[0].payload["doc_id"] if filt_hits else None,
        }
        rec["pass"] = rec["filtered_hits"] > 0
        results.append(rec)
        print(f"{qid}  base_hits={rec['baseline_hits']:2d}  filt_hits={rec['filtered_hits']:2d}  "
              f"base_top={rec['baseline_top_doc']}  filt_top={rec['filtered_top_doc']}")

    OUT_PATH.write_text(
        "\n".join(json.dumps(r) for r in results) + "\n",
        encoding="utf-8",
    )
    passed = sum(1 for r in results if r["pass"])
    print(f"\nWrote {len(results)} results to {OUT_PATH}")
    print(f"BENIGN PASS RATE: {passed} / {len(results)}")
    print(f"FALSE-DENIAL RATE: {len(results) - passed} / {len(results)}")


if __name__ == "__main__":
    main()
