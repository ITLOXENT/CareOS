Threat Model (CareOS)

Assets

- Patient data
- Clinical evidence and audit logs
- Access tokens and secrets

Trust Boundaries

- Public internet to ALB
- ALB to ECS service
- ECS service to database
- Internal admin access to cloud control plane

Threats and Mitigations

- Unauthorized access: enforce MFA, least privilege, audit logs.
- Data exfiltration: TLS, encrypted storage, export access controls.
- Tampering: audit log integrity, evidence hash chain, signed exports.
- Denial of service: rate limiting, WAF rules, autoscaling policies.

Implementation locations

- Auth and session controls: `apps/api/core/security.py`, `apps/web-admin/app/lib/auth.ts`.
- Tenant isolation: `apps/api/core/middleware.py`, `apps/api/core/rbac.py`.
- Audit logging: `apps/api/core/models/audit.py`, `apps/api/core/views/audit.py`.
- Evidence integrity: `apps/api/core/evidence.py`, `apps/api/core/views/evidence_packs.py`.
- Security headers: `apps/api/core/security.py`, `apps/web-admin/next.config.js`, `apps/web-portal/next.config.js`.
- Observability and request ids: `apps/api/careos_api/observability.py`, `apps/api/careos_api/logging.py`.

Evidence artifacts

- Audit exports: `apps/api/core/management/commands/export_audit_events.py`.
- Evidence pack generation logs and bundles.
- CI security checks: `.github/workflows/ci.yml`.
