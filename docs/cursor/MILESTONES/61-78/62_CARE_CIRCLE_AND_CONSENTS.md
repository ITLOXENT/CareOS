# 62_CARE_CIRCLE_AND_CONSENTS

## Cursor Agent Prompt

```text
Implement Care Circle (caregivers/next-of-kin) + consent/authorization model with audit trail and GDPR lawful-basis tracking.

Backend:
- Models: CareCircleMember (patient, person name, relationship, contact), ConsentRecord (patient, scope, lawful_basis, granted_by, expires_at).
- Endpoints:
  - GET/POST /patients/{id}/care-circle
  - PATCH/DELETE /patients/{id}/care-circle/{member_id}
  - GET/POST /patients/{id}/consents
  - POST /patients/{id}/consents/{consent_id}/revoke
- All writes create AuditEvent.

Frontend:
- web-portal: Patient detail tabs: Care Circle + Consents (CRUD).
- mobile: Patient detail: Care Circle (read-only MVP).

Tests:
- Consent scope enforcement test: endpoints requiring consent must fail without an active consent (use a simple rule for now: episodes.read requires consent if patient has a restricted flag).
```

## Verification Commands

```text
cd apps/api && uv run pytest -q
pnpm -r build
pnpm -r typecheck
pnpm run openapi:generate
pnpm run sdk:check
```

## Acceptance Checks

- Care Circle members can be managed.
- Consents can be granted/revoked and are audited.
- Consent rules block access when required.
- Tenant isolation verified.
