# 61_PATIENTS_AND_PROFILES

## Cursor Agent Prompt

```text
Implement core Patient + Contact/Profile domain end-to-end across API, web-portal, and mobile.

Backend (apps/api):
- Models: Patient, PatientIdentifier, PatientAddress, PatientContactMethod (tenant-scoped to Organization).
- Link Patient to Episodes (Episode.patient FK) without breaking existing endpoints.
- Endpoints (CRUD + search):
  - POST/GET /patients
  - GET/PATCH /patients/{id}
  - GET /patients/search?q=
  - GET /patients/{id}/episodes
- RBAC: only staff roles with PATIENT_READ/PATIENT_WRITE.

Frontend:
- apps/web-portal: Patient list + patient detail page with basic profile + episodes list.
- apps/mobile: Patient list + patient detail (read-only MVP) + pull-to-refresh.
- Use packages/sdk for all API calls and update OpenAPI + SDK.

Tests:
- Tenant isolation tests (cannot access patients across orgs).
- RBAC tests (read vs write).
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

- Patients can be created and searched.
- Episode can optionally reference a Patient.
- Web-portal and mobile display patient list/detail.
- SDK generation remains deterministic and CI passes.
