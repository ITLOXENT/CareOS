# Phase 40 — DATA_MODEL_POLISH_AND_INDEXING

## Cursor Agent Prompt
```text
Polish data model and performance basics.

Backend:
- Add indexes:
  - Episode(organization, created_at)
  - WorkItem(organization, status, due_at)
  - Notification(user, read_at)
  - AuditEvent(organization, created_at)
- Add default ordering for list endpoints (newest first).
- Add pagination for Episodes, WorkItems, Notifications, AuditEvents.
- Ensure endpoints accept `limit` and `cursor` (or `page`) consistently.
```

## Verification Commands
```text
cd apps/api
uv run pytest -q
```

## Acceptance Checks
- List endpoints paginate without breaking clients.
- Tests updated accordingly.


