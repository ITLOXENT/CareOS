# PHASE 25 — Integrations framework

## Cursor Agent Prompt

```text
Implement integrations framework + one real connector.

Backend:
- Integration model (tenant-scoped): provider, status, config_json (encrypted if utilities exist), last_tested_at, last_error.
- Endpoints:
  - GET /integrations
  - POST /integrations/{provider}/connect
  - POST /integrations/{provider}/test
  - POST /integrations/{provider}/disconnect
- Audit for connect/disconnect.
- Implement 1 provider end-to-end (email or sms).

Frontend (web-admin):
- Integrations page: connect form + test.

Tests:
- tenancy, validation, audit, no secrets in logs
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
- Admin can configure + test at least one integration provider.
- Audit events exist.
- Sensitive config not logged.

## Suggested Commit Message
`Phase 25: integrations framework`
