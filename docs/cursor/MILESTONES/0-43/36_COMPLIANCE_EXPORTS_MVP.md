# Phase 36 — COMPLIANCE_EXPORTS_MVP

## Cursor Agent Prompt
```text
Implement Compliance reporting MVP via exports.

Backend:
- ExportJob model (tenant-scoped):
  - organization, requested_by, kind, params_json, status(queued/running/done/failed), created_at, finished_at, artifact_path
- Implement synchronous export for now:
  - Episodes CSV export (last N days)
  - AuditEvents CSV export (last N days)
- Endpoints:
  - POST /exports (request export; returns job metadata)
  - GET /exports (list)
  - GET /exports/{id} (metadata)
  - GET /exports/{id}/download (serve file)
- RBAC:
  - Admin only
- Audit:
  - Export request and download are audited.

Frontend (web-admin):
- Admin Settings -> Exports page:
  - Request episodes/audit export for last 7/30/90 days
  - List jobs and download when ready
```

## Verification Commands
```text
cd apps/api
uv run pytest -q
pnpm -r build
```

## Acceptance Checks
- Admin can generate export and download it.
- Files are stored locally in dev under a safe path.
- Tenant isolation enforced.


