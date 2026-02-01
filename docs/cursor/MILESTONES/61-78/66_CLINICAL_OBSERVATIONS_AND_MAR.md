# 66_CLINICAL_OBSERVATIONS_AND_MAR

## Cursor Agent Prompt

```text
Implement observations/vitals + Digital MAR workflow, tenant-scoped and role-restricted.

Backend:
- Models: Observation (patient, type, value, unit, observed_at), MedicationOrder, MARAdministration (order, administered_at, dose, status).
- Endpoints:
  - POST/GET /patients/{id}/observations
  - POST/GET /patients/{id}/medications
  - POST /medications/{id}/administer
  - GET /patients/{id}/mar (timeline)
- MAR rules: cannot administer twice within configured window; record EpisodeEvent and AuditEvent.

Frontend:
- web-portal clinician view: patient observations + MAR timeline (MVP).
- mobile: patient observations + "record administration" (MVP if role allows).

Tests:
- MAR double-admin prevention.
- RBAC: only clinician roles can administer.
```

## Verification Commands

```text
cd apps/api && uv run pytest -q
pnpm -r build
pnpm -r typecheck
```

## Acceptance Checks

- Observations and MAR operate correctly and are audited.
- Role restrictions enforced.
