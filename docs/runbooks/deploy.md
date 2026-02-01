## Deploy runbook

### Preconditions

- Terraform applied for the target environment.
- Docker images built and pushed for API and web apps.
- Required secrets configured (DB, Stripe, admin session, audit).

### Deploy steps

1. Run the ECS deploy script:
   - `./scripts/deploy/ecs_deploy.sh`
2. Verify service health:
   - API: `/healthz/` and `/readyz/`
   - Web apps: load login pages
3. Confirm database migrations are applied.
4. Run smoke checks for critical flows (login, list episodes).

### Rollback

- Redeploy the previous task definition revision in ECS.
- Verify health endpoints return 200.
