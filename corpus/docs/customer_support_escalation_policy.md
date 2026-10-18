\---

doc\_id: customer\_support\_escalation\_policy

title: Customer Support Escalation Policy

sensitivity: public

allowed\_roles: \[employee, manager, sales, product]

allowed\_depts: \[engineering, product, sales, marketing, finance, hr, legal, exec]

marker: NW-PUB-SALES-0024-ESC

cross\_refs: \[handbook\_2026, customer\_churn\_analysis\_q2, sales\_playbook\_enterprise]

\---



\# Customer Support Escalation Policy



\## Severity Levels

\- P1: service down or data loss. Page on-call immediately.

\- P2: degraded performance (for example, latency spike). Respond within 1 hour.

\- P3: single-customer issue. Respond within 1 business day.



\## Escalation Path

Support, then Engineering on-call (P1/P2), then Engineering manager, then CTO. For enterprise accounts, loop in the AE per sales\_playbook\_enterprise.



\## Communication

Update the customer every 30 minutes for P1. Use the status page.



\## Root Cause

Every P1 gets a post-incident review within 5 business days. Latency-related incidents should reference the Q3 launch query-latency work as the durable fix.



\## Conduct

Support staff follow the Employee Handbook code of conduct. Abusive customer interactions are escalated to a manager, not handled alone.



\## Churn Prevention

Repeated P2s on an enterprise account should trigger a health check, informed by the themes in the internal churn analysis (latency, EMEA coverage).

