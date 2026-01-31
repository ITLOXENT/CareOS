NHS DSPT Mapping (Draft)

Purpose
Map DSPT assertions to CareOS controls, implementation locations, and evidence.

Assertion 1: Data Security and Protection Policies

- Control objective: Policies are documented, approved, and reviewed.
- Implementation location: `docs/compliance/retention-deletion-policy.md`, `docs/compliance/audit-log-policy.md`.
- Evidence artifacts: policy set, review logs, staff training record.
- Evidence generation: governance minutes, training completion exports.

Assertion 2: Data Access and System Security

- Control objective: Access is controlled and monitored.
- Implementation location: `apps/api/core/rbac.py`, `apps/api/core/middleware.py`, `apps/api/core/models.py`.
- Evidence artifacts: IAM roles, audit log policy, access reviews.
- Evidence generation: audit exports, access review sign-off.

Assertion 3: Data Quality and Information Governance

- Control objective: Data handling is accurate, complete, and traceable.
- Implementation location: `apps/api/core/models.py`.
- Evidence artifacts: validation rules, retention policy, change logs.
- Evidence generation: CI reports, data quality test results.

Assertion 4: Incident Response and Continuity

- Control objective: Incidents are managed and learned from.
- Implementation location: `docs/compliance/isms/incident-response-plan.md`.
- Evidence artifacts: incident response plan, post-incident reviews.
- Evidence generation: tabletop exercise records, incident ticket exports.
