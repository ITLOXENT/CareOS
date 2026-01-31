HIPAA Security Rule Mapping (Draft)

Purpose
Map HIPAA Security Rule safeguards to CareOS controls, implementation locations, and evidence.

Administrative Safeguards

- Control objective: Security management process and workforce training.
- Implementation location: `docs/compliance/isms/incident-response-plan.md`, `docs/compliance/audit-log-policy.md`.
- Evidence artifacts: policies, training records, risk assessments.
- Evidence generation: governance reviews, training exports.

Physical Safeguards

- Control objective: Facility and device security responsibilities (cloud provider).
- Implementation location: `docs/architecture/infra.md`.
- Evidence artifacts: cloud compliance reports, access controls.
- Evidence generation: provider compliance documentation, audit reports.

Technical Safeguards

- Control objective: Access control, audit controls, integrity, transmission security.
- Implementation location: `apps/api/core/rbac.py`, `apps/api/core/models.py`, `apps/api/core/middleware.py`, `docs/architecture/infra.md`.
- Evidence artifacts: IAM roles, audit log policy, TLS config.
- Evidence generation: CI checks, configuration reviews, log exports.
