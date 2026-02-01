# Phase 42 — PRODUCTION_READINESS_CHECKLIST

## Cursor Agent Prompt
```text
Create a production readiness checklist and ensure docs reflect reality.

- Add `docs/production/readiness.md`:
  - Environments
  - Secrets
  - Logging redaction
  - Backups
  - Migration procedures
  - Rollback plan
  - Security headers
  - Incident response basics
- Add `docs/production/deploy.md` describing a vendor-neutral deploy flow (no AWS specifics).
- Ensure all doc paths match real file paths.
```

## Verification Commands
```text
pnpm -r build
pnpm -r typecheck
cd apps/api && uv run pytest -q
```

## Acceptance Checks
- Docs exist and reference real paths.
- Verification commands still pass.


