## Production readiness checklist

### Environments

- Define `dev`, `stage`, and `prod` environments with separate databases.
- Set `DJANGO_ENV=production` and `DJANGO_DEBUG=false` for prod.
- Confirm `ALLOWED_HOSTS` and `DJANGO_CSRF_TRUSTED_ORIGINS` are set.

### Secrets

- `DJANGO_SECRET_KEY`
- `ADMIN_SESSION_SECRET`
- `ADMIN_USERNAME` and `ADMIN_PASSWORD`
- `ADMIN_AUDIT_SECRET` and `ADMIN_AUDIT_ORG_ID`
- `STRIPE_SECRET_KEY` and `STRIPE_WEBHOOK_SECRET`
- `EMAIL_BACKEND` and `DEFAULT_FROM_EMAIL`

### Logging redaction

- Redaction in `apps/api/careos_api/logging.py` covers tokens, cookies, and PII fields.
- Logs include `request_id` via `careos_api/observability.py`.

### Backups

- Follow `docs/runbooks/backup-restore.md`.
- Verify backup frequency and restore verification.

### Migration procedures

- Run `uv run python manage.py migrate` before app start.
- Validate with `uv run pytest -q` in `apps/api`.

### Rollback plan

- Keep last known-good release artifact and env config.
- Roll back by re-deploying previous artifact and re-running migrations if needed.

### Security headers

- API headers in `apps/api/core/security.py`.
- Web headers in `apps/web-admin/next.config.js` and `apps/web-portal/next.config.js`.

### Incident response

- Follow `docs/runbooks/incident-response.md`.
