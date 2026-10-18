from pathlib import Path

lines = Path("ingest.py").read_text(encoding="utf-8").splitlines()
new_block = '''    # Build chunk records first, embed, then construct PointStruct with vector.
    chunk_records = []
    for path, doc in parsed:
        meta = doc["meta"]
        chunks = chunk_body(doc["body"])
        for i, chunk in enumerate(chunks):
            text_for_embedding = f"{meta['title']}\\n\\n{chunk}"
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
        ))'''.splitlines()

new_lines = lines[:118] + new_block + lines[157:]
Path("ingest.py").write_text("\n".join(new_lines), encoding="utf-8")
print(f"ingest.py patched: {len(lines)} lines -> {len(new_lines)} lines")
