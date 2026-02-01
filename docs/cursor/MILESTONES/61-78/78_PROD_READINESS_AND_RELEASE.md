# 78_PROD_READINESS_AND_RELEASE

## Cursor Agent Prompt

```text
Production readiness pass.

Backend:
- Ensure all migrations exist and are deterministic.
- Add smoke test script (DB migrate + create org + create episode + create work item).
- Add monitoring hooks: structured logs, basic health endpoints, readiness checks.
- Update RUNBOOK/README with clean local dev instructions.

Frontend:
- Ensure env var validation and clear startup errors.
- Add minimal error boundary pages.

CI:
- Ensure pipelines run full test/build suite.

Deliverables:
- Release checklist + threat model updates.
```

## Verification Commands

```text
cd apps/api && uv run pytest -q
pnpm -r build
pnpm -r typecheck
```

## Acceptance Checks

- One-command local bring-up works.
- CI green.
- Release checklist exists.
- No files exceed line limits after refactors.
