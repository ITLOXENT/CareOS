# CareOS — Cursor Master Instruction (Phases 29–42)

Date: 2026-02-01

Operating mode:
- Work strictly in-repo. No new external services unless explicitly instructed by a phase.
- No placeholders. If a feature is out of scope for the phase, omit it cleanly.
- Keep changes minimal and consistent with existing architecture.
- Always run verification commands at the end of each phase and paste raw output.
- If a phase fails, fix it before moving to the next phase.

Repo invariants:
- Deterministic OpenAPI at repo root: `openapi.json`
- SDK generation must run from repo root via `pnpm run sdk:generate` / `pnpm run sdk:check`
- Web apps call API only through `packages/sdk`
- Tenant context is enforced server-side
- RBAC is authoritative server-side; UI hides routes but does not enforce security

Verification baseline:
- `cd apps/api && uv run pytest -q`
- `pnpm -r typecheck`
- `pnpm -r build`
