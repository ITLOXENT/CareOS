# Phase 41 — SMOKE_E2E_SCRIPT

## Cursor Agent Prompt
```text
Add a deterministic smoke script to validate the MVP user journey (dev only).

- Add `scripts/smoke/e2e_admin.sh`:
  - Creates an org + admin user in dev DB (via a management command or existing setup function)
  - Creates an episode
  - Transitions it through at least 2 states
  - Assigns and completes a work item
  - Uploads evidence and links it
  - Lists notifications and marks read
  - Creates an audit export and downloads it
- Script must be deterministic, safe to re-run, and exit non-zero on failure.
```

## Verification Commands
```text
bash scripts/smoke/e2e_admin.sh
cd apps/api && uv run pytest -q
pnpm -r build
```

## Acceptance Checks
- Script runs end-to-end without manual steps (aside from having dev env running).
- Produces clear pass/fail output.


