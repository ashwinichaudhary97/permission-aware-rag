---

doc_id: engineering_onboarding_wiki

title: Engineering Onboarding Wiki

sensitivity: internal

allowed_roles: [employee, manager, product]

allowed_depts: [engineering, product]

marker: NW-INT-ENG-0004-EOW

cross_refs: [product_roadmap_q3, it_security_policy]

---



# Engineering Onboarding Wiki



## Repo and Service Map

Our monorepo is northwind/core. Services: ingest, enrichment, query-api, billing, admin-console. Each service has an OWNERS file. Start by reading ingest and query-api; they carry most traffic.



## Local Dev

Use the devcontainer. Run make bootstrap then make test. The staging environment is refreshed nightly; credentials live in 1Password under Eng Staging.



## Deploy Process

Trunk-based development. Every PR needs one approval and green CI. Deploys to staging are automatic; prod deploys require a release captain and a change ticket. See the runbook engineering_deploy_runbook for rollback steps.



## Security Notes

Never log customer PII. The IT Security Policy applies to all internal tooling, including local scripts that touch production data. Use the shared secrets manager; no secrets in code or .env files.



## Q3 Priorities

This quarter engineering focus is the ingest pipeline rewrite and query latency reduction, both driven by the Q3 product roadmap. See product_roadmap_q3 for the customer-facing commitments.

