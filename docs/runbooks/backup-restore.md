Backup and Restore Runbook

Purpose
Provide steps to back up and restore CareOS data stores.

Backup
1) Verify automated backups are enabled for primary databases.
2) Trigger an on-demand snapshot for the target environment.
3) Export audit logs using `python manage.py export_audit_events --org-slug <slug>`.

Restore
1) Create a new restore point (snapshot) before changes.
2) Restore the database snapshot into a new instance.
3) Update application configuration to point to the restored instance.
4) Run smoke tests via `python3 scripts/smoke_test.py`.

Validation
- Confirm service health endpoints respond.
- Verify sample records and audit logs.
