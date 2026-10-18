# Permission-Aware RAG: Row-Level Access Control for Enterprise Retrieval

A minimal, reproducible RAG system that demonstrates a common enterprise failure - silent permission leakage - and fixes it with an ACL pre-filter at the retrieval layer.

## Problem

Baseline RAG retrieves documents by semantic similarity alone. When the corpus contains documents at different access levels (public, internal, confidential, restricted), a normal user's query can retrieve a restricted document and pass it to the LLM. The LLM summarizes it accurately. No error is raised. The log shows a successful query. The leak is silent.

This project measures that failure mode and fixes it.

## Corpus

29 synthetic documents from a fictional B2B SaaS company, split across four sensitivity tiers:

| Tier | Count | Example |
|---|---|---|
| Public | 7 | Handbook, IT security policy, onboarding guide |
| Internal | 10 | Engineering wiki, product roadmap, deploy runbook |
| Confidential | 5 | Financial forecast, churn analysis, pricing strategy |
| Restricted | 7 | Board minutes, exec comp plan, layoff list, M&A target |

Each document carries YAML frontmatter with doc_id, sensitivity, allowed_roles, allowed_depts, and a unique marker string used for leak detection.

## Test sets (frozen before any filter code)

- corpus/redteam/set_v1.jsonl - 10 privilege-escalation queries. Each targets a specific forbidden document. Frozen at commit 9b7a8f3, before ACL filter design began.
- corpus/benign/set_v1.jsonl - 6 legitimate queries that must succeed. Used to measure false-denial rate.

The freeze ordering is verifiable: git log shows the query commit is the oldest, predating all corpus, index, and filter code.

## Results

Measured on 29 docs / 60 chunks, embedding = BAAI/bge-small-en-v1.5 (384-dim, cosine), top-k = 10, ACL semantics = AND (user must match allowed_roles AND allowed_depts).

| Metric | Baseline (no filter) | Filtered (ACL pre-filter) |
|---|---|---|
| Red-team leaks | 10 / 10 | 0 / 10 |
| Retrieval hits per query | 10 | 10 |
| Benign pass rate | 6 / 6 | 6 / 6 |
| False-denial rate | - | 0 / 6 |

What the numbers mean:

- 10 to 0 leaks: the filter blocks every privilege-escalation attempt.
- Hits stay at 10: the filter does not kill retrieval; it redirects it to allowed documents. A query that would have retrieved a restricted document still returns 10 valid results, just from documents the user is allowed to see.
- 6/6 benign pass: the filter does not break legitimate usage.

## The clearest single row in the data

ben_006 - query: "How does the RIF process work and how is severance calculated?", user = HR employee.

| Version | Top retrieved document | Answers the question? | Leaks? |
|---|---|---|---|
| Baseline | layoff_list_2026 (restricted) | Yes | Yes |
| Filtered | handbook_2026 (public) | Yes | No |

Same query, same user, same retrieval count. The baseline retrieves the restricted layoff list. The filter retrieves the public handbook, which describes the same RIF process and severance formula. Both answer the question; only one leaks.

## Method

1. Freeze the attack surface. Red-team and benign queries committed to git before any filter code exists.
2. Index the corpus. Parse YAML frontmatter into Qdrant payload. Chunk with 800-character window, 100-character overlap. Embed with BGE-small, prepending the document title to each chunk for context.
3. Measure baseline. Run the 10 red-team queries against Qdrant with no filter. Log retrieved doc_ids and marker strings. Baseline: 10/10 queries retrieved a forbidden document.
4. Implement ACL pre-filter. Add a Qdrant payload filter to the query: allowed_roles contains user role AND allowed_depts contains user department. Forbidden chunks never enter the candidate set.
5. Re-measure. Same 10 queries, same corpus, same embedding. Only the filter differs. Filtered: 0/10 leaks, hits unchanged.
6. Measure benign cost. Run the 6 benign queries through both versions. Confirm the filter does not deny legitimate access.

## Why pre-filter instead of post-filter

Post-filtering (retrieve top-k first, then drop unauthorized results) also stops leaks, but it wastes top-k slots on chunks the user cannot see. When a query top-10 contains 7 forbidden chunks, post-filter leaves 3 valid results. Pre-filter preserves all 10 by excluding forbidden chunks before the ranking runs.

Pre-filter also embeds the ACL in the payload, so filtering costs no extra query time. Qdrant evaluates the filter during vector search, not after.

## Repository structure

The repository contains:

- corpus/docs/ - 29 documents, one per file
- corpus/redteam/set_v1.jsonl - 10 frozen privilege-escalation queries
- corpus/benign/set_v1.jsonl - 6 frozen benign control queries
- ingest.py - parse corpus, embed, upsert to Qdrant
- baseline_query.py - measure leaks without ACL filter
- filtered_query.py - measure leaks with ACL pre-filter
- benign_query.py - measure false-denial rate
- baseline_results.jsonl - per-query results, no filter
- filtered_results.jsonl - per-query results, with filter
- benign_results.jsonl - per-query benign results

## Setup

Requires Python 3.10+, Docker (for Qdrant), and the packages qdrant-client, sentence-transformers, pyyaml.

Start Qdrant:

    docker run -d --name qdrant -p 6333:6333 qdrant/qdrant

Set up Python:

    python -m venv .venv
    .venv\Scripts\activate
    pip install qdrant-client sentence-transformers pyyaml

Index the corpus:

    python ingest.py --reset

Run the three measurements:

    python baseline_query.py
    python filtered_query.py
    python benign_query.py

## Scope and limitations

This is a controlled test bed, not a production benchmark.

- Corpus size. 29 documents is enough to demonstrate the failure mode and verify the fix; it is not enough to claim production scaling. The measurement methodology (freeze queries, run baseline, run filter, compare) extends directly to larger corpora.
- Synthetic content. Documents are fictional and designed so that each red-team query has exactly one forbidden document containing the answer. This ensures the before/after comparison is measurable, not accidental.
- ACL semantics. The filter uses AND (role AND department must both match). Documents intentionally include role and department mismatches (customer_churn_analysis_q2 allows the manager role but excludes the hr department; pricing_strategy_2026 allows the manager role but excludes the product department) so the AND choice is testable, not just asserted.
- Not covered. Reference-following attacks (a public document naming a restricted doc_id in its body), prompt injection, and multi-turn conversation state. These are documented failure surfaces, not implemented defenses.

## Design decisions

Title prepended to chunks before embedding. The embedding vector captures document context, not just chunk content. A chunk that says "bonus target is 40 percent of base" embeds closer to "executive compensation plan" if the title is prepended.

Marker strings for leak detection. Each document carries a unique opaque string (for example NW-REST-EXEC-0007-ECP). Leak detection checks whether the LLM output or retrieved chunks contain a forbidden marker. This is falsifiable: no marker means no leak, regardless of what the LLM says.

Fail-closed frontmatter validation. ingest.py rejects any document missing required ACL fields. A malformed document fails the ingest; it does not silently disappear from the index. This is deliberate, because a silently skipped document corrupts the leak measurement.
