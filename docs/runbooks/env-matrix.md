## Environment matrix

### Environments

- `dev`: local development and smoke tests.
- `stage`: pre-production validation.
- `prod`: production workloads.

### Required env vars (API)

- `DJANGO_SECRET_KEY`
- `DJANGO_ENV`
- `DJANGO_DEBUG`
- `DJANGO_ALLOWED_HOSTS`
- `DJANGO_CSRF_TRUSTED_ORIGINS`
- `ADMIN_AUDIT_SECRET`
- `ADMIN_AUDIT_ORG_ID`
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `EMAIL_BACKEND`
- `DEFAULT_FROM_EMAIL`
- `SENTRY_DSN` (if enabled)
- `SENTRY_ENVIRONMENT`
- `SENTRY_RELEASE`
- `SENTRY_TRACES_SAMPLE_RATE`

### Required env vars (web-admin)

- `ADMIN_USERNAME`
- `ADMIN_PASSWORD`
- `ADMIN_SESSION_SECRET`
- `ADMIN_ROLE`
- `ADMIN_ORG_NAME`
- `ADMIN_ORG_ID` (optional)
- `NEXT_PUBLIC_API_BASE_URL`

### Required env vars (web-portal)

- `NEXT_PUBLIC_API_BASE_URL`

### Optional env vars

- `SENTRY_SEND_DEFAULT_PII`
- `ADMIN_MFA_REQUIRED`
- `ADMIN_TOTP_SECRET`
