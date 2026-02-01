# PHASE 21 — Audit + events query APIs

## Cursor Agent Prompt

```text
Harden compliance-grade audit querying.

Backend:
- AuditEvent endpoints:
  - GET /audit-events (filters: actor, action, date range, target)
- Ensure stable ordering + pagination (created_at + id).
- Ensure EpisodeEvent/EvidenceEvent remain append-only and pageable.

Frontend (web-admin):
- Admin Settings -> Audit tab/page.

Tests:
- tenant isolation
- pagination stability
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
- Audit events are queryable tenant-scoped.
- Stable pagination/order verified by tests.

## Suggested Commit Message
`Phase 21: audit/events query`
