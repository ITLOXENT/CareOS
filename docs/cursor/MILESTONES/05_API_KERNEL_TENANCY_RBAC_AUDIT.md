# 05_API_KERNEL_TENANCY_RBAC_AUDIT

## Cursor Agent Prompt
```text
Implement backend core kernel in apps/api.

Implement:
- Tenancy: Organization, Site, Team
- Identity: User, Membership
- RBAC: roles and permission checks
- Middleware sets tenant context (org) and enforces org scoping
- AuditEvent append-only
- Base API: /health, /me, /orgs/current, /audit-events (read-only with RBAC)
- Logging redaction for sensitive fields
- Strict settings for dev/test/prod

Testing:
- Unit tests for tenant scoping and RBAC decisions
- Tests for AuditEvent creation on writes

Update compliance docs with real file paths for implemented controls.

```

## Verification Commands
```text
cd apps/api && uv run ruff check .
cd apps/api && uv run mypy .
cd apps/api && uv run pytest -q

```

## Acceptance Checks
- Creating an Organization and Membership is possible via management command or admin-only endpoint.
- Requests without tenant context are rejected (except public endpoints).
- /me returns current user and tenant context.
- AuditEvent is created on any write operation and is queryable with RBAC.

