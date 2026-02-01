# Phase 35 — AI_REVIEW_QUEUE_SHELL

## Cursor Agent Prompt
```text
Implement AI Review queue shell (human-in-the-loop).

Backend:
- AIReviewItem model (tenant-scoped):
  - organization, episode (FK nullable), kind, payload_json, status(pending/approved/rejected), created_at, decided_at, decided_by nullable
- Endpoint:
  - GET /ai-review-items (pending only by default)
  - POST /ai-review-items/{id}/decide (approve/reject with note)
- RBAC:
  - Admin/Staff can view; decide is Admin-only unless a permission already exists
- Audit:
  - Decide creates AuditEvent

Frontend (web-admin):
- AI Review page:
  - List pending items
  - Detail view showing payload
  - Approve/Reject actions if authorized
```

## Verification Commands
```text
cd apps/api
uv run pytest -q
pnpm -r build
```

## Acceptance Checks
- AI Review page lists pending items from API via SDK.
- Approve/Reject works and is audited.


