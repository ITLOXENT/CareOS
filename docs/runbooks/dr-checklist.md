## Disaster recovery (DR) checklist

### Targets

- RTO (restore time objective): 4 hours.
- RPO (recovery point objective): 1 hour.

### Pre-incident readiness

- Verify automated database backups are enabled.
- Verify backup retention and restore procedures in `backup-restore.md`.
- Ensure on-call access to infra credentials and runbooks.
- Confirm release artifacts are available for rollback.

### During incident

1) Declare incident and assign Incident Commander.
2) Identify blast radius and affected services.
3) Determine whether to fail over, restore, or roll back.
4) Preserve logs and audit evidence.

### Recovery steps

1) Restore database from latest snapshot to a new instance.
2) Update service configuration to point to restored DB.
3) Run migrations if required.
4) Run smoke tests and confirm health endpoints.
5) Monitor error rate, latency, and queue depth.

### Post-recovery

- Document root cause and timeline.
- Update runbooks and test plans.
- Review RTO/RPO performance vs targets.
