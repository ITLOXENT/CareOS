# PHASE 17 — Patient directory (tenant-scoped)

## Cursor Agent Prompt

```text
Implement Patient Directory MVP (staff-only).

Backend:
- Patient model (tenant-scoped):
  - organization FK
  - given_name, family_name
  - date_of_birth (nullable)
  - nhs_number (nullable string; validate; unique per org when present)
  - phone/email (nullable)
  - address fields (nullable)
  - created_at/updated_at
- Endpoints:
  - POST /patients
  - GET /patients (search; pagination)
  - GET /patients/{id}
  - POST /patients/{id}/merge (MVP; emits AuditEvent)

RBAC:
- ADMIN/STAFF: create/read/merge
- VIEWER: read only

Frontend (web-admin):
- Patients page: search + list + create
- Episode create: optionally select a patient

Tests:
- CRUD access tests
- tenancy isolation
- merge permission test

Update OpenAPI + regenerate SDK/types.
```

## Verification Commands

```text
pnpm run openapi:generate
pnpm run sdk:check
pnpm -r typecheck
pnpm -r build
cd apps/api && uv run pytest -q
```

## Acceptance Checks
- Staff can create/search/view patients in web-admin.
- Episode creation can link to a patient.
- Merge emits an audit trail.
- Tenant isolation tests pass.

## Suggested Commit Message
`Phase 17: patient directory`
