# Phase 38 — OBSERVABILITY_AND_LOGGING

## Cursor Agent Prompt
```text
Add observability baseline.

Backend:
- Structured logging (JSON) in prod; human-readable in dev.
- Request id correlation (middleware) and include in responses and logs.
- /health includes: version/build sha (env), timestamp, and DB connectivity (safe).
- Add pagination for AuditEvent list endpoint (if present).

Frontend:
- Show request id for API errors on web-admin error states.
```

## Verification Commands
```text
cd apps/api
uv run pytest -q
pnpm -r build
```

## Acceptance Checks
- Logs include request_id for every request.
- /health returns deterministic keys and safe values.


