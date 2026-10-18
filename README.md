\# Permission-Aware RAG - Methodology Log



\## Freeze policy

The red-team and benign query sets are frozen BEFORE ACL filter design begins, to prevent circular evaluation. Query files must not be edited after the freeze commit. Any additions go into new versioned files (set\_v2.jsonl), never by editing set\_v1.jsonl.



\## Freeze log

\- 2026-10-18 - corpus/redteam/set\_v1.jsonl (10 queries) and corpus/benign/set\_v1.jsonl (6 queries) frozen. No ACL filter code exists at this commit.



\## Why

If queries were written after seeing the filter, the result would be circular. Freezing them in git first makes the result falsifiable.



\## Status

\- Documents generated: 10 (of 100 planned)

\- Red-team frozen: 10 (of 50 planned)

\- Benign frozen: 6 (of 30 planned)

\- ACL filter: not yet implemented

