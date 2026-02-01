# 74_REPORTING_AND_DASHBOARDS

## Cursor Agent Prompt

```text
Implement reporting layer: operational dashboards (SLA, workload, outcomes), export CSV/JSON, and query optimization.

Backend:
- Add /reports endpoints for:
  - workload summary (work items by status/assignee)
  - SLA breaches
  - episode throughput
  - medication adherence (if MAR enabled)
- Add caching for heavy reports (per-tenant keys).
- Ensure RBAC: only REPORT_READ roles.

Frontend:
- web-admin dashboard uses reports endpoints.
- basic charts/tables (no fancy UI required).

Tests:
- Report tenant isolation and RBAC.
```

## Verification Commands

```text
cd apps/api && uv run pytest -q
pnpm -r build
pnpm -r typecheck
```

## Acceptance Checks

- Reports render and export.
- Performance acceptable (cached).
- RBAC enforced.
