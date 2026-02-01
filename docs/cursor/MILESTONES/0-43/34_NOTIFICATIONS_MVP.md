# Phase 34 — NOTIFICATIONS_MVP

## Cursor Agent Prompt
```text
Implement Notifications MVP (in-app + email plumbing).

Backend:
- Notification model (tenant-scoped):
  - organization, user, kind, title, body, read_at nullable, created_at
- Triggers:
  - When WorkItem assigned -> notify assignee
  - When Episode transitions -> notify assigned_to (if any) and created_by
- Endpoints:
  - GET /notifications (filters: unread_only)
  - POST /notifications/{id}/read
- Email:
  - Provide email sending interface (no external provider wiring); implement console backend in dev/test.
  - Ensure sensitive fields are redacted in logs.

Frontend (web-admin):
- Notifications page:
  - List notifications
  - Mark as read
  - Show unread badge in nav (optional)
```

## Verification Commands
```text
cd apps/api
uv run pytest -q
pnpm -r build
```

## Acceptance Checks
- Assignment and transition events create notifications.
- Notifications list is tenant-scoped and user-scoped.
- Mark-read works and is RBAC safe.


