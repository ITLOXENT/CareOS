## Deployment flow (vendor-neutral)

### Prerequisites

- Build artifacts for API and web apps are available.
- Environment variables and secrets are configured for target environment.
- Database is reachable and backups are current.

### Deploy steps

1. Apply database migrations:
   - `cd apps/api && uv run python manage.py migrate`
2. Deploy API service:
   - Roll out new container or process.
   - Verify `/healthz/` and `/readyz/` return 200.
3. Deploy web apps:
   - `apps/web-admin` and `apps/web-portal` artifacts.
4. Run smoke checks:
   - `bash scripts/smoke/e2e_admin.sh`
5. Monitor logs and error rates for at least 15 minutes.

### Rollback

- Redeploy the previous artifact version.
- Re-run migrations only if a rollback migration exists.
- Confirm `/healthz/` and `/readyz/` are healthy.
