---

doc_id: product_roadmap_q3

title: Q3 Product Roadmap

sensitivity: internal

allowed_roles: [employee, manager, product, exec]

allowed_depts: [engineering, product, sales, marketing, exec]

marker: NW-INT-PROD-0005-RMP

cross_refs: [marketing_launch_plan, finance_forecast_2026, engineering_onboarding_wiki]

---



# Q3 Product Roadmap



## Theme: Faster Signals

The Q3 theme is delivering faster, cleaner supply-chain signals to enterprise customers. Two flagship bets: the ingest pipeline rewrite and query latency reduction to sub-200ms p95.



## Committed Initiatives

1. Ingest rewrite: 3x throughput, targets the top-10 enterprise accounts. Engineering owner: Data Platform.

2. Query latency: p95 from 480ms to below 200ms. Blocks the Enterprise tier launch.

3. Supplier risk score v2: new model, marketed in the Q3 launch.



## Launch Plan

The Q3 launch is scheduled for the second week of September, coordinated with Marketing. The marketing launch plan (marketing_launch_plan) defines the announcement sequence, and the 2026 finance forecast (finance_forecast_2026) assumes the launch drives 6.2M USD in new enterprise ARR in Q3-Q4. Any scope change to the launch must be reviewed against the forecast assumptions with Finance.



## Dependencies and Risks

- Ingest rewrite is on the critical path for the launch.

- Query latency work depends on the new index service.

- Hiring for two backend roles is pending headcount approval (see Finance).



## Out of Scope

Mobile app redesign, international expansion beyond EMEA.

