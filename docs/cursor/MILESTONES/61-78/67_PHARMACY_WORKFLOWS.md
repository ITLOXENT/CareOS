# 67_PHARMACY_WORKFLOWS

## Cursor Agent Prompt

```text
Implement pharmacy-facing workflows (MVP): prescription queue, dispensing checklist, interventions, and handover notes.

Backend:
- Models: PrescriptionRequest, DispenseChecklistItem, PharmacyIntervention, HandoverNote.
- Endpoints:
  - POST/GET /prescriptions (queue)
  - POST /prescriptions/{id}/transition (received -> dispensing -> ready -> collected)
  - GET/POST /prescriptions/{id}/checklist
  - POST /prescriptions/{id}/interventions
  - POST /prescriptions/{id}/handover
- Each transition/appends AuditEvent + EpisodeEvent if linked to episode/patient.

Frontend:
- web-portal pharmacy section: queue list + detail.
- web-admin: admin view-only list.

Tests:
- Transition validation.
- Tenant isolation.
```

## Verification Commands

```text
cd apps/api && uv run pytest -q
pnpm -r build
pnpm -r typecheck
```

## Acceptance Checks

- Pharmacy queue can be processed end-to-end.
- Checklist/interventions/handover captured and audited.
