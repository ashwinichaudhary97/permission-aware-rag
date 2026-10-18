---

doc_id: engineering_deploy_runbook

title: Production Deploy Runbook

sensitivity: internal

allowed_roles: [employee, manager]

allowed_depts: [engineering, product]

marker: NW-INT-ENG-0023-DRB

cross_refs: [engineering_onboarding_wiki, it_security_policy, product_roadmap_q3]

---



# Production Deploy Runbook



## Pre-Deploy

- Change ticket approved.

- Release captain assigned.

- Feature flags set per engineering_onboarding_wiki process.

- No deploys during the Q3 launch freeze window (second week of September) without CTO approval.



## Deploy Steps

1. Merge to trunk, CI green.

2. Deploy to staging, run smoke tests.

3. Canary 5 percent for 30 minutes.

4. Ramp 25 percent, 50 percent, 100 percent.

5. Monitor error rate and p95 latency (target below 200ms for query-api per product_roadmap_q3).



## Rollback

Flip feature flag off; if service-level, redeploy previous tag. Page on-call if error rate above 2 percent.



## Security

Deploy credentials come from the secrets manager, never .env. The IT Security Policy applies; log access is audited.



## Post-Deploy

Update the changelog. Post in the eng-deploys channel.

