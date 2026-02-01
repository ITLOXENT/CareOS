# 08_EPISODES_AND_INBOX

## Cursor Agent Prompt

```text
Implement Episodes and Work Inbox end-to-end.

Backend:
- Episode model (tenant-scoped)
- EpisodeEvent model (append-only timeline)
- WorkItem model (inbox task)
- State machine with explicit transitions
- Endpoints:
  - POST /episodes
  - GET /episodes
  - GET /episodes/{id}
  - POST /episodes/{id}/transition
  - GET /episodes/{id}/timeline
  - GET /work-items
  - POST /work-items/{id}/assign
  - POST /work-items/{id}/complete

Frontend (web-admin):
- Inbox page with filters (status, assignee, SLA)
- Episode detail page with timeline and transitions
- Create episode flow

Tests:
- Transition validation tests
- RBAC tests for access

```

## Verification Commands

```text
cd apps/api && uv run pytest -q
pnpm -r build

```

## Acceptance Checks

- Staff can create an episode, view it in inbox, transition state, and see timeline events.
- Every transition creates EpisodeEvent and AuditEvent.
- Tenant isolation is verified by tests.
