# PHASE 19 — Notifications + SLA escalations

## Cursor Agent Prompt

```text
Implement in-app notifications and SLA escalation jobs.

Backend:
- Notification model (tenant-scoped): org, recipient, title/body/url, unread/read, created_at/read_at.
- WorkItem: use `sla_breach_at`; background job notifies for breached/soon.

Infra:
- Wire background worker (Celery + Redis) if not already.
- Scheduled task checks SLAs.

Endpoints:
- GET /notifications
- POST /notifications/{id}/read

Frontend (web-admin):
- Notifications page
- Inbox SLA badges
- Topbar unread indicator

Tests:
- deterministic SLA escalation test (time control)
- RBAC + tenancy

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
- Work items nearing SLA breach produce notifications.
- Notifications visible in web-admin and can be marked read.
- Background job is wired and deterministic tests exist.

## Suggested Commit Message
`Phase 19: notifications + sla`
