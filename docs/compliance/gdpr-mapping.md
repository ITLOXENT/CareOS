## GDPR mapping

### Right to access

- Endpoint: `GET /privacy/dsar/exports/`, `POST /privacy/dsar/export/`, download link.
- Procedure: Generate DSAR export and provide artifact to requester.
- Evidence: export job records and audit events.

### Right to rectification

- Endpoint: `PATCH /orgs/current/`, patient updates via admin UI.
- Procedure: Update stored records and log audit event.
- Evidence: audit events for changes.

### Right to erasure

- Endpoint: `POST /privacy/dsar/delete/`.
- Procedure: Anonymize patient/user data where deletion is not lawful.
- Evidence: `privacy.patient.anonymized` and `privacy.user.anonymized` audit events.

### Right to restriction of processing

- Endpoint: Admin settings and role controls.
- Procedure: Disable user or restrict access by role.
- Evidence: audit events for role changes and deactivation.

### Data portability

- Endpoint: DSAR export bundle download.
- Procedure: Provide JSON export artifact.
- Evidence: DSAR export records.

### Breach notification

- Procedure: Incident response runbook.
- Evidence: incident records and communications log.
