# 43_DB_MIGRATIONS_EPISODES_INBOX

## Cursor Agent Prompt

```text
Fix Episode/WorkItem migrations + pytest DB setup (green tests).

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

- Phase 43 deliverables are implemented.
- All verification commands pass (green).
- No new monolithic files created; any touched file >400 lines must be split as part of the phase.

### Phase-specific requirements
Backend
- Ensure Episode/EpisodeEvent/WorkItem tables exist in test DB.
- Ensure migrations are created and applied under pytest.
- Remove/neutralize any migration-disabling config (`--nomigrations`, MIGRATION_MODULES overrides, etc.)
- Add a clear failing-test -> green-test fix path.

Tests
- `tests/test_episodes.py` must pass.
- Add a regression test that asserts `Episode._meta.db_table` exists in DB during pytest (or equivalent).

Notes
- Prefer fixing config and real migrations rather than hacks.
