# 54_OBSERVABILITY

## Cursor Agent Prompt

```text
Observability: structured logs, metrics, tracing hooks, error reporting (Sentry-ready).

CONTEXT
- Repo: CareOS monorepo
- Coding rules: keep files <= 400 lines where practical; split by domain; no placeholder logic in security/compliance paths.
- Do NOT introduce broad exception handling.
- Keep API tenant-scoped: organization derived from active membership.
- Server remains authoritative; UI must never assume permissions.

TASKS
1) Implement the phase deliverables precisely (backend + frontend as applicable).
2) Update OpenAPI + deterministic SDK generation outputs if endpoints/types change.
3) Add/adjust tests so verification commands are green.

DELIVERABLES
- Concrete code changes
- Updated OpenAPI + SDK artifacts when required
- Passing verification commands
```

## Verification Commands

```text
cd apps/api && uv run pytest -q
pnpm -r typecheck
pnpm -r build
pnpm run openapi:generate
pnpm run sdk:check
```

## Acceptance Checks

- Phase 54 deliverables are implemented.
- All verification commands pass (green).
- No new monolithic files created; any touched file >400 lines must be split as part of the phase.

### Phase-specific requirements
Observability
- Structured JSON logging with request_id + org_id + user_id (when available).
- Metrics endpoint (Prometheus-style or simple JSON).
- Error reporting wiring (Sentry-ready; env-controlled).
- Audit log correlation with request_id.

Tests
- Request id present in responses/log context.
