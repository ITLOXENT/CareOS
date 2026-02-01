# PHASE 28 — Ops readiness

## Cursor Agent Prompt

```text
Ops readiness milestone.

Backend:
- Structured JSON logging + correlation/request id.
- Health endpoints: /healthz and /readyz.
- CI gates:
  - fail on OpenAPI drift (openapi:generate then git diff)
  - fail on SDK drift (sdk:check)
  - run backend tests + web builds
- Runbooks: deploy, backup/restore, monitoring.

Frontend:
- ensure prod builds for web-admin and web-portal
- minimal error boundaries

Acceptance:
- CI is “red if drift” for schema/SDK.
- Health endpoints work.
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
- CI fails on OpenAPI/SDK drift.
- Health endpoints exist and are wired.
- Runbooks exist and are usable.
- Builds and tests pass reliably.

## Suggested Commit Message
`Phase 28: ops readiness`
