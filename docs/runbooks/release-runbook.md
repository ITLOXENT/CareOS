## Release runbook

### Deploy checklist

- Confirm all CI checks are green (format, typecheck, tests, build).
- Verify `openapi.json` and SDK drift checks are clean.
- Confirm `DJANGO_ENV` and `DJANGO_DEBUG` are correct for the target env.
- Verify required secrets are present (see Env matrix).
- Ensure database backups are healthy before deploy.

### Deployment steps

1) Build and publish the release artifact (API + web-admin + web-portal).
2) Apply infrastructure changes (Terraform) if required.
3) Run migrations:
   - `cd apps/api && uv run python manage.py migrate`
4) Deploy services.
5) Run smoke tests:
   - `python3 scripts/smoke_test.py`

### Post-deploy validation

- `GET /healthz/` returns 200.
- `GET /readyz/` returns 200.
- Login works for web-admin and portal.
- Check logs for 5xx spikes and auth failures.

### Rollback procedure

1) Re-deploy the last known good release artifact.
2) Revert config/env vars if changed.
3) If migrations were applied, verify compatibility:
   - Prefer forward-fix; only down-migrate if required.
4) Re-run smoke tests.
