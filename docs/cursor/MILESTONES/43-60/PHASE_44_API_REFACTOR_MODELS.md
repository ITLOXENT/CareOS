# 44_API_REFACTOR_MODELS

## Cursor Agent Prompt

```text
Split monolithic core/models.py into domain modules (episodes, inbox, evidence, audit, orgs).

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

- Phase 44 deliverables are implemented.
- All verification commands pass (green).
- No new monolithic files created; any touched file >400 lines must be split as part of the phase.

### Phase-specific requirements
Backend
- Split `apps/api/core/models.py` into `apps/api/core/models/` package:
  - episodes.py (Episode, EpisodeEvent, transition logic)
  - inbox.py (WorkItem + assignment/complete)
  - evidence.py (placeholder until phase 47 if not yet implemented)
  - audit.py (AuditEvent if present)
  - orgs.py (Organization/Membership if currently in core)
- Keep public imports stable by re-exporting in `core/models/__init__.py`.
- Update any imports across codebase.
