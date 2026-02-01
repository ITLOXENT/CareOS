## Privacy & GDPR controls

### Consent records

- Store consent decisions with `subject_type`, `subject_id`, `consent_type`, `policy_version`, and channel.
- Endpoints:
  - `GET /privacy/consents/`
  - `POST /privacy/consents/`

### DSAR export

- Admins can export data for a subject (patient or org) to a JSON artifact.
- Endpoints:
  - `GET /privacy/dsar/exports/`
  - `POST /privacy/dsar/export/`
  - `GET /privacy/dsar/exports/{export_id}/download/`

### DSAR delete (anonymize)

- Admins can request anonymization for a subject.
- Patient data is anonymized (names, contact details, identifiers cleared).
- Episodes are detached from patient and redacted.
- Endpoint:
  - `POST /privacy/dsar/delete/`

### Retention

- `retention_class` and `retention_until` fields exist on key entities.
- Scheduled purge job anonymizes patients/episodes and deletes evidence files
  when retention is due.
