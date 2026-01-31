# 03_INFRA_TERRAFORM_BASELINE

## Cursor Agent Prompt
```text
Build AWS Terraform baseline with secure defaults and environment separation.

Implement infra/terraform:
- modules/ for network, security, db, compute, observability
- envs/dev, envs/stage, envs/prod
- remote state backend definition
- VPC, private subnets, NAT, VPC endpoints as appropriate
- RDS Postgres with KMS encryption, backups, PITR
- ECS Fargate service skeleton (api + web placeholders are fine only at infra level; app must be real later)
- ALB + WAF + ACM TLS
- CloudWatch logs and alarms
- Secrets Manager usage pattern

Documentation:
- docs/architecture/infra.md: describe resources, threat assumptions, and boundaries.

No manual console steps required.

```

## Verification Commands
```text
cd infra/terraform && terraform fmt -recursive
cd infra/terraform/envs/dev && terraform init -backend=false
cd infra/terraform/envs/dev && terraform validate

```

## Acceptance Checks
- Terraform code is formatted and validates.
- envs are separated and modules exist.
- docs/architecture/infra.md exists with a clear diagram and notes.

