# PHASE 20 — Admin settings (team/roles)

## Cursor Agent Prompt

```text
Implement Admin Settings: org/team/users/roles.

Backend:
- Endpoints:
  - org profile read/update limited fields
  - list org members
  - invite user (signed token + expiry)
  - change role
  - deactivate membership
- ADMIN only for writes.
- AuditEvent for every action.

Frontend (web-admin):
- Admin Settings tabs:
  - Organization
  - Team
  - Invites

Tests:
- RBAC enforcement
- token expiry
- tenant isolation

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
- Org admin can invite user, change role, deactivate membership.
- Non-admin cannot access these actions.
- Audit events exist for all actions.

## Suggested Commit Message
`Phase 20: admin settings`
