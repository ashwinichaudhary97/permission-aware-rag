"""
ingest.py - Load Northwind corpus into Qdrant.

Reads corpus/docs/*.md, parses YAML frontmatter into a payload,
chunks the body text, embeds with BGE-small, upserts into Qdrant.

Usage:
    python ingest.py            # create collection and upsert (fails if exists)
    python ingest.py --reset    # drop and recreate collection first
"""

import argparse
import re
import sys
from pathlib import Path

import yaml
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from sentence_transformers import SentenceTransformer

COLLECTION = "northwind"
DOCS_DIR = Path("corpus/docs")
QDRANT_URL = "http://localhost:6333"
EMBED_MODEL = "BAAI/bge-small-en-v1.5"
EMBED_DIM = 384
CHUNK_SIZE = 800       # characters, not tokens - simple v1
CHUNK_OVERLAP = 100


def parse_doc(path: Path) -> dict:
    """Split YAML frontmatter from body. Frontmatter must start at line 1 with '---'."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError(f"{path}: missing YAML frontmatter (must start with '---')")
    # Split on the second '---' line
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"{path}: frontmatter not closed with '---'")
    frontmatter = yaml.safe_load(parts[1])
    body = parts[2].strip()

    # Required keys
    for key in ("doc_id", "title", "sensitivity", "allowed_roles",
                "allowed_depts", "marker", "cross_refs"):
        if key not in frontmatter:
            raise ValueError(f"{path}: missing required key '{key}'")

    return {"meta": frontmatter, "body": body}


def chunk_body(body: str) -> list[str]:
    """Simple fixed-size character chunker with overlap. Good enough for v1."""
    if len(body) <= CHUNK_SIZE:
        return [body]
    chunks = []
    start = 0
    while start < len(body):
        end = min(start + CHUNK_SIZE, len(body))
        chunks.append(body[start:end])
        if end == len(body):
            break
        start = end - CHUNK_OVERLAP
    return chunks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Drop collection first")
    args = parser.parse_args()

    if not DOCS_DIR.exists():
        print(f"ERROR: {DOCS_DIR} not found. Run from project root.", file=sys.stderr)
        return 1

    md_files = sorted(DOCS_DIR.glob("*.md"))
    if not md_files:
        print(f"ERROR: no .md files in {DOCS_DIR}", file=sys.stderr)
        return 1

    print(f"Found {len(md_files)} documents in {DOCS_DIR}")

    # Parse all docs first (fail fast on bad frontmatter)
    parsed = []
    for path in md_files:
        try:
            parsed.append((path, parse_doc(path)))
        except Exception as e:
            print(f"ERROR parsing {path}: {e}", file=sys.stderr)
            return 1
    print(f"Parsed all {len(parsed)} documents OK")

    # Load embedding model
    print(f"Loading embedding model {EMBED_MODEL} ...")
    model = SentenceTransformer(EMBED_MODEL)
    print("Model loaded")

    # Connect to Qdrant
    client = QdrantClient(url=QDRANT_URL)
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION in existing:
        if args.reset:
            print(f"Dropping existing collection '{COLLECTION}' ...")
            client.delete_collection(COLLECTION)
        else:
            print(
                f"ERROR: collection '{COLLECTION}' already exists. "
                f"Run with --reset to recreate.",
                file=sys.stderr,
            )
            return 1

    print(f"Creating collection '{COLLECTION}' ...")
    client.create_collection(
        collection_name=COLLECTION,
        vectors_config=VectorParams(size=EMBED_DIM, distance=Distance.COSINE),
    )

    # Build chunk records first, embed, then construct PointStruct with vector.
    chunk_records = []
    for path, doc in parsed:
        meta = doc["meta"]
        chunks = chunk_body(doc["body"])
        for i, chunk in enumerate(chunks):
            text_for_embedding = f"{meta['title']}\n\n{chunk}"
            chunk_records.append({
                "payload": {
                    "doc_id": meta["doc_id"],
                    "title": meta["title"],
                    "sensitivity": meta["sensitivity"],
                    "allowed_roles": meta["allowed_roles"],
                    "allowed_depts": meta["allowed_depts"],
                    "marker": meta["marker"],
                    "chunk_index": i,
                    "chunk_count": len(chunks),
                    "text": chunk,
                    "text_for_embedding": text_for_embedding,
                },
                "text_for_embedding": text_for_embedding,
            })

    print(f"Embedding {len(chunk_records)} chunks ...")
    embeddings = model.encode(
        [r["text_for_embedding"] for r in chunk_records],
        batch_size=32,
        show_progress_bar=True,
        normalize_embeddings=True,
    )

    points = []
    for idx, (record, vec) in enumerate(zip(chunk_records, embeddings)):
        points.append(PointStruct(
            id=idx,
            vector=vec.tolist(),
            payload=record["payload"],
        ))

    print(f"Upserting {len(points)} points to Qdrant ...")
    client.upsert(collection_name=COLLECTION, points=points)

    info = client.get_collection(COLLECTION)
    print(f"Done. Collection '{COLLECTION}' has {info.points_count} points.")

    # Sanity: count unique doc_ids
    unique_docs = {p.payload["doc_id"] for p in points}
    print(f"Distinct doc_ids ingested: {len(unique_docs)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())