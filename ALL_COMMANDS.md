# All Commands — Phases 29–42 (Local)

Run phases one by one. After each phase, commit and push.

Baseline:
- cd apps/api && uv run pytest -q
- pnpm -r typecheck
- pnpm -r build

OpenAPI/SDK:
- pnpm run openapi:generate
- pnpm run sdk:generate
- pnpm run sdk:check

Recommended commit pattern:
- git status
- git add -A
- git commit -m "phase-XX: <title>"
- git push
