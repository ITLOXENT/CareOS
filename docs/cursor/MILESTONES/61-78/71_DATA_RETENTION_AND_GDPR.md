# 71_DATA_RETENTION_AND_GDPR

## Cursor Agent Prompt

```text
Implement GDPR capabilities: DSAR export, data retention policies, and right-to-erasure workflows with legal holds.

Backend:
- DSAR export job: for a Patient or User, generate export bundle (JSON + metadata), store as Document, track status.
- Erasure workflow: soft-delete + anonymize PII where allowed; block if legal hold active.
- Endpoints:
  - POST /gdpr/dsar (start)
  - GET /gdpr/dsar/{id}
  - POST /gdpr/erase (start)
  - GET /gdpr/erase/{id}
- Ensure AuditEvent for all actions.

Frontend:
- web-admin Admin Settings: GDPR tab (start DSAR/erasure, view status).

Tests:
- Legal hold blocks erasure.
- DSAR includes required linked objects.
```

## Verification Commands

```text
cd apps/api && uv run pytest -q
pnpm -r build
```

## Acceptance Checks

- DSAR export generates a bundle.
- Erasure anonymizes data safely.
- All actions audited and tenant-safe.
