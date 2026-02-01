# CareOS Runbook (Phases 29–42)

This pack continues from the earlier phases and drives CareOS to a shippable, production-ready baseline.

## Standard loop per phase
1) Apply the phase prompt in Cursor (single phase at a time)
2) Run verification commands for that phase
3) Fix failures until green
4) Commit with an explicit message `phase-XX: <title>`
5) Push

## Repo root commands
- OpenAPI:
  - `pnpm run openapi:generate`
- SDK:
  - `pnpm run sdk:generate`
  - `pnpm run sdk:check`
- Typecheck/build:
  - `pnpm -r typecheck`
  - `pnpm -r build`
- API tests:
  - `cd apps/api && uv run pytest -q`

## Environment notes
- `apps/api` uses `uv` environment. Use `DJANGO_SETTINGS_MODULE=careos_api.settings.<env>` for management commands.
- `apps/web-admin` and `apps/web-portal` are Next.js apps.
- `packages/types` and `packages/sdk` are TypeScript workspace packages.

## Definition of "done"
A phase is done only when:
- All acceptance checks pass
- All verification commands pass
- Code is committed and pushed
