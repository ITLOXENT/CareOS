# PHASE 16 — Episodes + Inbox end-to-end

## Cursor Agent Prompt

```text
Implement Episodes and Work Inbox end-to-end (finish the spec properly).

Backend (apps/api/core):
- Episode model: tenant-scoped; fields: id, organization, patient(optional), title, description, status, created_by, assigned_to(optional), created_at, updated_at.
- EpisodeEvent model: append-only timeline; fields: id, organization, episode FK, event_type, payload_json, created_by(optional), created_at.
- WorkItem model: inbox task; fields: id, organization, episode(optional), kind, status, assigned_to(optional), due_at(optional), sla_breach_at(optional), created_by(optional), created_at, completed_at(optional).

State machine:
- Episode statuses: new, triage, in_progress, blocked, resolved, closed.
- Explicit transitions in one place with validation.
- Transition endpoint enforces transitions and writes EpisodeEvent + AuditEvent.

Endpoints:
- POST /episodes
- GET /episodes (filters: status, assigned_to, created_by, search by title)
- GET /episodes/{id}
- POST /episodes/{id}/transition
- GET /episodes/{id}/timeline
- GET /work-items (filters: status, assigned_to, SLA)
- POST /work-items/{id}/assign
- POST /work-items/{id}/complete

RBAC + tenancy:
- Auth required; org membership required.
- ADMIN: full, STAFF: read/write, VIEWER: read-only.
- Enforce org scoping in DB queries.

Events:
- Every transition creates EpisodeEvent + AuditEvent.
- Work item assign/complete emits AuditEvent.

Frontend (apps/web-admin):
- Inbox page with filters and links to episode detail.
- Episode list page with create flow.
- Episode detail page: timeline + transition buttons + assign/complete.

SDK usage:
- All calls via `@careos/sdk`.

Tests (apps/api/tests):
- Transition validation tests
- RBAC tests
- Tenant isolation tests

Update OpenAPI and regenerate SDK/types after adding endpoints.
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
- Staff can create an episode, see it in Episodes/Inbox, transition state, and see timeline events.
- Every transition writes EpisodeEvent and AuditEvent.
- WorkItem assign/complete writes AuditEvent.
- Tenant isolation verified by tests.
- OpenAPI updated + SDK regenerated without drift.

## Suggested Commit Message
`Phase 16: episodes + inbox end-to-end`
