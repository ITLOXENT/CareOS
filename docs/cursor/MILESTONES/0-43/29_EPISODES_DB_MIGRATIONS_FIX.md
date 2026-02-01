# Phase 29 — EPISODES_DB_MIGRATIONS_FIX

## Cursor Agent Prompt
```text
Fix failing Episode tests due to missing tables.

- Ensure `Episode`, `EpisodeEvent`, `WorkItem` live in `apps/api/core/models.py` and are included in migrations.
- Create and commit core migrations that include these tables:
  - `core_episode`
  - `core_episodeevent`
  - `core_workitem`
- Ensure pytest runs migrations (no migration-disabling flags).
- Add/adjust pytest configuration so test database includes latest core migrations.

Deliver:
- Migration file(s) under `apps/api/core/migrations/`
- If needed, `apps/api/conftest.py` to enforce migrations
- Update tests if they assumed old table names or endpoints.
```

## Verification Commands
```text
cd apps/api
DJANGO_SETTINGS_MODULE=careos_api.settings.test uv run python manage.py makemigrations core
DJANGO_SETTINGS_MODULE=careos_api.settings.test uv run python manage.py showmigrations core
DJANGO_SETTINGS_MODULE=careos_api.settings.test uv run python manage.py migrate
uv run pytest -q
```

## Acceptance Checks
- `uv run pytest -q` passes.
- Episode-related tests no longer fail with `no such table`.


