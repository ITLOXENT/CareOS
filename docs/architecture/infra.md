CareOS Infrastructure Baseline

Overview
This baseline defines a multi-environment AWS layout with clear network boundaries,
private compute, encrypted data stores, and managed observability.

Environments

- dev, stage, prod live in `infra/terraform/envs/`
- Remote state uses S3 + DynamoDB locking (configured in each env backend)

High-level diagram

Internet
|
v
ALB (TLS, WAF)
|
v
ECS Fargate (private subnets)
|
v
RDS Postgres (private subnets, KMS)

Key resources

- VPC with public and private subnets, NAT gateway, and S3 VPC endpoint
- ALB with HTTPS listener, WAFv2, and security groups
- ECS Fargate cluster, task definition, and service
- RDS Postgres with KMS encryption, backups, and PITR
- CloudWatch log groups and CPU alarms
- Secrets Manager for database credentials

Threat assumptions and boundaries

- Public ingress is limited to ALB on 443
- Application and database traffic stay inside the VPC
- Secrets are stored in Secrets Manager and encrypted with KMS
- Logs are retained in CloudWatch for auditability
