## ISO 27001 control mapping

### A.5 Policies for information security

- Objective: Policies are documented and reviewed.
- Implementation: `docs/compliance/README.md`, `docs/compliance/retention-deletion-policy.md`.
- Evidence: policy documents, review records.
- Owner: Security lead.

### A.6 Organization of information security

- Objective: Roles and responsibilities are defined.
- Implementation: `docs/runbooks/release-runbook.md`, `docs/runbooks/incident-response.md`.
- Evidence: runbook approvals, on-call roster.
- Owner: Ops lead.

### A.8 Asset management

- Objective: Assets and data handling are tracked.
- Implementation: `apps/api/core/models.py`, `docs/compliance/retention-deletion-policy.md`.
- Evidence: data inventory, retention schedules.
- Owner: Compliance lead.

### A.9 Access control

- Objective: Access is restricted and audited.
- Implementation: `apps/api/core/rbac.py`, `apps/api/core/middleware.py`.
- Evidence: audit logs, access reviews.
- Owner: Security lead.

### A.12 Operations security

- Objective: Logging, monitoring, and change control.
- Implementation: `apps/api/careos_api/logging.py`, `docs/runbooks/monitoring.md`.
- Evidence: log samples, alert configs.
- Owner: Ops lead.

### A.14 System acquisition, development, and maintenance

- Objective: Secure SDLC and testing.
- Implementation: `.github/workflows/ci.yml`, `docs/runbooks/smoke-tests.md`.
- Evidence: CI logs, test reports.
- Owner: Engineering lead.

### A.16 Information security incident management

- Objective: Incidents are handled and reviewed.
- Implementation: `docs/runbooks/incident-response.md`.
- Evidence: incident tickets, postmortems.
- Owner: Incident commander.

### A.17 Business continuity

- Objective: DR planning and backups.
- Implementation: `docs/runbooks/backup-restore.md`, `docs/runbooks/dr-checklist.md`.
- Evidence: restore tests, backup logs.
- Owner: Ops lead.
