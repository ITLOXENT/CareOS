# 46_EPISODES_INBOX_COMPLETE

## Cursor Agent Prompt

```text
Complete Episodes + Work Inbox endpoints, transitions, timeline, and tenant isolation.

CONTEXT
- Repo: CareOS monorepo
- Coding rules: keep files <= 400 lines where practical; split by domain; no placeholder logic in security/compliance paths.
- Do NOT introduce broad exception handling.
- Keep API tenant-scoped: organization derived from active membership.
- Server remains authoritative; UI must never assume permissions.

TASKS
1) Implement the phase deliverables precisely (backend + frontend as applicable).
2) Update OpenAPI + deterministic SDK generation outputs if endpoints/types change.
3) Add/adjust tests so verification commands are green.

DELIVERABLES
- Concrete code changes
- Updated OpenAPI + SDK artifacts when required
- Passing verification commands
```

## Verification Commands

```text
cd apps/api && uv run pytest -q
pnpm -r typecheck
pnpm -r build
pnpm run openapi:generate
pnpm run sdk:check
```

## Acceptance Checks

- Phase 46 deliverables are implemented.
- All verification commands pass (green).
- No new monolithic files created; any touched file >400 lines must be split as part of the phase.

### Phase-specific requirements
Backend
- Endpoints must exist and be tenant-scoped:
  - POST /episodes
  - GET /episodes
  - GET /episodes/{id}
  - POST /episodes/{id}/transition
  - GET /episodes/{id}/timeline
  - GET /work-items
  - POST /work-items/{id}/assign
  - POST /work-items/{id}/complete
- State machine with explicit transitions; reject invalid transitions with 400.
- Every transition must create:
  - EpisodeEvent (append-only timeline)
  - AuditEvent (who/what/when, tenant-scoped)

Frontend (web-admin)
- Inbox page: filters (status, assignee, SLA), list, open episode.
- Episode detail: timeline + allowed transitions + perform transition.
- Create episode flow.

Tests
- Transition validation tests
- RBAC tests
- Tenant isolation tests
