from pathlib import Path
p = Path("baseline_query.py")
text = p.read_text(encoding="utf-8")
old = '''        hits = client.search(
            collection_name=COLLECTION,
            query_vector=vec,
            limit=TOP_K,
            with_payload=True,
        )

        retrieved_doc_ids = [h.payload["doc_id"] for h in hits]'''
new = '''        response = client.query_points(
            collection_name=COLLECTION,
            query=vec,
            limit=TOP_K,
            with_payload=True,
        )
        hits = response.points

        retrieved_doc_ids = [h.payload["doc_id"] for h in hits]'''
if old not in text:
    print("ERROR: old block not found")
else:
    text = text.replace(old, new)
    p.write_text(text, encoding="utf-8")
    print("patched")
