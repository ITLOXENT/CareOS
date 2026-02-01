# Phase 39 — CI_GATES_AND_DRIFT_CHECKS

## Cursor Agent Prompt
```text
Tighten CI to prevent drift and regressions.

- Ensure CI runs:
  - `pnpm run openapi:generate` then fails if openapi.json changes
  - `pnpm run sdk:check`
  - `pnpm -r typecheck`
  - `pnpm -r build`
  - `cd apps/api && uv run pytest -q`
```

## Verification Commands
```text
pnpm -r typecheck
pnpm -r build
cd apps/api && uv run pytest -q
pnpm run openapi:generate
pnpm run sdk:check
```

## Acceptance Checks
- CI fails if OpenAPI/SDK drift exists.
- Local verification commands pass.


