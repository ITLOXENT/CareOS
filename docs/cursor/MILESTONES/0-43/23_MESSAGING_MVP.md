# PHASE 23 — Messaging MVP

## Cursor Agent Prompt

```text
Implement messaging MVP.

Backend:
- Conversation (tenant-scoped): participants, optional episode link.
- Message (tenant-scoped): conversation, sender, body, created_at, read receipts minimal.
- Endpoints:
  - POST /conversations
  - GET /conversations
  - GET /conversations/{id}
  - POST /conversations/{id}/messages
  - POST /messages/{id}/read
- AuditEvent for sends (metadata only).

Frontend:
- web-admin: messages tab on episode or separate page.

Tests:
- RBAC, tenancy, basic send/read
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
- Staff can create conversation, send messages, mark read.
- Messages are tenant-scoped and protected.
- Audit metadata exists.

## Suggested Commit Message
`Phase 23: messaging mvp`
