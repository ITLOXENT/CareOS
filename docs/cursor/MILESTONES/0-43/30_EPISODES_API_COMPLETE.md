# Phase 30 — EPISODES_API_COMPLETE

## Cursor Agent Prompt
```text
Implement tenant-scoped Episodes API end-to-end (MVP but real).

Backend:
- Episode model (tenant-scoped) fields: id, organization(FK), title, description, status, created_by(FK), assigned_to(FK nullable), created_at
- EpisodeEvent model (append-only timeline): episode(FK), actor(FK), event_type, from_status, to_status, note, created_at
- State machine with explicit transitions (central function/table):
  - new -> triage
  - triage -> in_progress
  - in_progress -> waiting
  - waiting -> in_progress
  - in_progress -> resolved
  - resolved -> closed
  - any -> cancelled (admin only)
- WorkItem model (inbox task): organization, episode(FK), kind, status(open/assigned/done), assigned_to(FK), due_at, created_at, completed_at
- Endpoints:
  - POST /episodes
  - GET /episodes
  - GET /episodes/{id}
  - POST /episodes/{id}/transition
  - GET /episodes/{id}/timeline
- RBAC:
  - Admin: full access
  - Staff: list/read; transition if assigned or in triage; cannot cancel
  - Viewer: read-only (no create/transition)
- Audit:
  - Every write creates AuditEvent.
  - Every transition creates EpisodeEvent AND AuditEvent in same request.

Keep implementation consistent with existing patterns in apps/api/core/views.py and middleware tenant context.
```

## Verification Commands
```text
cd apps/api
uv run python manage.py migrate
uv run pytest -q
```

## Acceptance Checks
- POST /episodes creates episode within current tenant.
- GET /episodes returns only tenant-scoped episodes.
- POST /episodes/{id}/transition validates transition table and RBAC, writes EpisodeEvent + AuditEvent.
- GET /episodes/{id}/timeline returns ordered EpisodeEvents.
- Tests cover invalid transitions and RBAC decisions.


