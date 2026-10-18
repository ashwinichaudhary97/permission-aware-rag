---

doc_id: incident_response_plan

title: Security Incident Response Plan

sensitivity: internal

allowed_roles: [employee, manager, legal, exec]

allowed_depts: [engineering, legal, exec]

marker: NW-INT-ENG-0027-IRP

cross_refs: [it_security_policy, investigation_report_2026, data_retention_policy]

---



# Security Incident Response Plan



## Severity

- SEV1: confirmed breach of confidential/restricted data.

- SEV2: suspected breach or credential compromise.

- SEV3: policy violation, no data exposure.



## Roles

Incident commander (Security lead), comms lead (Legal), exec sponsor (CTO).



## Steps

1. Detect and report within 1 hour per the IT Security Policy.

2. Contain (isolate hosts, revoke tokens).

3. Eradicate and recover.

4. Notify: Legal assesses regulatory notification; Exec approves external comms.

5. Post-incident review within 5 business days.



## Investigation Handoff

If the incident involves an employee, Legal opens an internal investigation (pattern from investigation_report_2026). Preserve evidence per data_retention_policy legal hold.



## Communication

No external communication without Legal plus Exec approval. Customers notified per contract SLA.



## Drills

Tabletop exercise twice a year.

