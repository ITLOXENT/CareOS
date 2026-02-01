# Phase 31 — WORK_INBOX_API_COMPLETE

## Cursor Agent Prompt
```text
Implement Work Inbox endpoints and assignment/complete lifecycle.

Backend:
- Endpoints:
  - GET /work-items (filters: status, assignee, due_before, kind)
  - POST /work-items/{id}/assign (assign to current user or specified user within org; RBAC admin/staff)
  - POST /work-items/{id}/complete (mark done; only assignee or admin)
- On episode creation: create a default WorkItem(kind="episode_triage") with status=open, due_at = now + SLA default (configurable)
- On episode transition to resolved/closed/cancelled: auto-complete remaining open WorkItems for that episode (record AuditEvent)
- Ensure tenant isolation on WorkItem queries and writes.
```

## Verification Commands
```text
cd apps/api
uv run pytest -q
```

## Acceptance Checks
- Inbox list works and is tenant-scoped.
- Assignment and completion enforce RBAC and tenant membership.
- Auto-created WorkItem exists for new episodes.
- AuditEvent created for assign/complete operations.


