# PHASE 15 — Fix Episode DB migrations + pytest

## Cursor Agent Prompt

```text
Fix failing Episode tests: `no such table: core_episode`.

Goal:
- Ensure Episode/EpisodeEvent/WorkItem models exist AND migrations are created and applied in pytest.
- Ensure pytest always applies migrations in test runs (no migration disabling).
- Ensure `core` app is correctly installed and migrations are discoverable.

Requirements:
1) Migrations
- If missing: create Django migrations for core models (Episode, EpisodeEvent, WorkItem).
- Commit migration files under `apps/api/core/migrations/`.

2) Pytest configuration hardening
- Confirm pytest-django runs migrations.
- Remove any migration-disabling configuration.
- Add deterministic configuration/fixture so migrations always run.

3) Tenancy invariant
- Episode and WorkItem must be org-scoped (organization_id FK).

Deliverables:
- New/updated migration(s)
- Updated pytest config (if needed)
- All backend tests pass

Do not change test expectations to “make it pass”; fix the underlying migrations/config.
```

## Verification Commands

```text
cd apps/api && uv run pytest -q
```

## Acceptance Checks
- `uv run pytest -q` passes.
- `python manage.py showmigrations core` shows core migrations applied in test DB.
- `core_episode` table exists during tests (no OperationalError).

## Suggested Commit Message
`Phase 15: fix episode migrations + pytest`
