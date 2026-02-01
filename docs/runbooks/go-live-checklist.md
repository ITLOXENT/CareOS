## Go-live checklist

### Sign-off

- Engineering lead approval: ______________________  Date: __________
- Security lead approval: _________________________  Date: __________
- Compliance lead approval: _______________________  Date: __________
- Product owner approval: _________________________  Date: __________

### Pre-launch

- All CI checks are green.
- Threat model reviewed and updated.
- Pen-test checklist completed and findings remediated.
- DR checklist reviewed and backup restore tested.
- Env matrix validated for target environment.
- Sentry and monitoring configured.

### Launch

- Migrations applied.
- Services deployed and healthy.
- Smoke tests completed.

### Post-launch

- Monitor error rate and latency for 24 hours.
- Verify audit log and evidence exports.
- Confirm on-call escalation path.
