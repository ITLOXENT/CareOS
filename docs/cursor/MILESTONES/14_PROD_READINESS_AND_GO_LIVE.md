# 14_PROD_READINESS_AND_GO_LIVE

## Cursor Agent Prompt
```text
Finalize production readiness and go-live pipeline.

Implement:
- Observability: structured logs, metrics, tracing hooks
- Runbooks:
  - incident response
  - backup/restore
  - access reviews
- CI/CD:
  - terraform plan on PR
  - apply with approval for stage/prod
  - deploy services
  - post-deploy smoke tests
- Evidence generation:
  - audit export command
  - evidence pack generation in running environment

Acceptance:
- One-click stage deploy and smoke test
- Evidence artifacts can be produced from stage

```

## Verification Commands
```text
cd infra/terraform && terraform fmt -recursive
cd infra/terraform/envs/dev && terraform validate

```

## Acceptance Checks
- Stage environment deploys from CI with approvals.
- Smoke tests run and pass.
- Evidence artifacts generation is documented and runnable.

