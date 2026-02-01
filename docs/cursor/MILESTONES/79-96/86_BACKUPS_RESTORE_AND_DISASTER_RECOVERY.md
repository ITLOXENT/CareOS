# 86_BACKUPS_RESTORE_AND_DISASTER_RECOVERY

## Cursor Agent Prompt

```text
Implement Backups Restore And Disaster Recovery.

Goals:
- Backup/restore automation, restore drills, RPO/RTO targets, and DR runbooks.

Non-negotiables:
- Keep existing API contracts stable unless explicitly extended.
- Preserve tenant isolation, audit logging, and RBAC checks.
- No placeholder endpoints: if a feature is declared, wire it end-to-end.

Deliverables:
- Backend changes (Django/DRF + migrations as needed)
- Frontend changes (web-admin + web-portal as applicable)
- SDK/types regeneration if contracts change
- Tests for critical paths and tenant isolation
```

## Verification Commands

```text
cd apps/api && uv run pytest -q
pnpm -r typecheck
pnpm -r build
```

## Acceptance Checks

- Feature works end-to-end in local dev.
- RBAC and tenant isolation verified by tests.
- OpenAPI regenerated (if endpoints changed) and SDK check passes.
- No files > 400 LOC added; refactor if needed.
