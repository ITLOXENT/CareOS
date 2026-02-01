# PHASE 18 — Evidence MVP

## Cursor Agent Prompt

```text
Implement Evidence (upload + tagging + linking) MVP.

Backend:
- EvidenceItem model (tenant-scoped): org, optional episode/patient links, title, kind, file metadata, sha256, tags, created_by, created_at.
- EvidenceEvent model (append-only).
- Storage: use existing storage abstraction; otherwise implement minimal interface (local dev + S3-ready).

Endpoints:
- POST /evidence
- GET /evidence (filters: episode, patient, tags, kind)
- GET /evidence/{id}
- POST /evidence/{id}/link
- POST /evidence/{id}/tag

Events + audit:
- Every evidence operation emits EvidenceEvent + AuditEvent.

RBAC:
- ADMIN/STAFF: create/link/tag/read
- VIEWER: read only

Frontend (web-admin):
- Evidence page listing + filters
- Episode detail: Evidence section showing linked evidence + link/upload

Tests:
- RBAC, tenancy, linking events

OpenAPI + SDK update.
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
- Staff can upload/link evidence to an episode and see it on episode detail.
- Evidence actions create EvidenceEvent + AuditEvent.
- Tenant isolation verified by tests.

## Suggested Commit Message
`Phase 18: evidence mvp`
