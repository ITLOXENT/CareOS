# 04_COMPLIANCE_PACK

## Cursor Agent Prompt
```text
Create compliance documentation pack aligned to NHS DTAC, DSPT, clinical safety, GDPR, HIPAA, and ISO 27001 readiness.

Create docs/compliance:
- dtac-mapping.md
- dspt-mapping.md
- dcb0129-clinical-safety-plan.md
- hipaa-security-rule-mapping.md
- isms/ (iso 27001 readiness folder)
  - risk-register-template.md
  - control-mapping-template.md
  - incident-response-plan.md
- threat-model.md
- data-flow-diagrams.md
- audit-log-policy.md
- retention-deletion-policy.md

Each mapping must include:
- control objective
- implementation location placeholders must be explicit and later replaced with real file paths
- evidence artifacts and how to generate them

```

## Verification Commands
```text
ls -la docs/compliance

```

## Acceptance Checks
- All required docs exist and contain substantive content (not outlines).
- Each mapping doc includes control objectives and evidence generation sections.
- No empty sections.

