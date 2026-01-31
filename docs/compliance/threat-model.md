Threat Model (Draft)

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

- Unauthorized access: enforce strong authentication, least privilege, audit logs.
- Data exfiltration: encrypt at rest and in transit, monitor egress.
- Tampering: immutable logs, integrity checks, KMS-backed secrets.
- Denial of service: WAF, rate limiting, autoscaling policies.

Implementation location: pending (replace with specific repo path).
Evidence artifacts: threat model review notes, mitigations list, CI security scans.
