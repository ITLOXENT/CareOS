## Pen-test checklist

### Pre-test

- Confirm scope (web-admin, web-portal, API, mobile).
- Validate staging environment mirrors production controls.
- Obtain test accounts and test data sets.
- Confirm logging and alerting are enabled.
- Agree on testing window and escalation contacts.

### Authentication and sessions

- Brute force and rate limit checks.
- Session fixation and replay checks.
- MFA enforcement (when configured).
- Logout and session revocation behavior.

### Authorization and tenancy

- Tenant isolation validation on all endpoints.
- Role enforcement for admin/staff/viewer.
- Verify portal endpoints cannot access staff resources.

### Input validation

- Injection checks (SQL, command, template).
- File upload validation and content type enforcement.
- JSON schema handling and error responses.

### Data protection

- TLS enforced on all endpoints.
- Evidence and export artifact access checks.
- Audit log integrity verification.

### API abuse

- Pagination limits and query parameter bounds.
- Rate limiting on auth endpoints.
- Error leakage (no secrets in responses).

### Post-test

- Capture findings with severity and repro steps.
- Create remediation tickets with owners.
- Retest fixes and record validation evidence.
