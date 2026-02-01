# 55_COMPLIANCE_REPORTING

## Cursor Agent Prompt

```text
Compliance reporting: evidence bundles, scheduled reports, exports, submission tracking.

CONTEXT
- Repo: CareOS monorepo
- Coding rules: keep files <= 400 lines where practical; split by domain; no placeholder logic in security/compliance paths.
- Do NOT introduce broad exception handling.
- Keep API tenant-scoped: organization derived from active membership.
- Server remains authoritative; UI must never assume permissions.

TASKS
1) Implement the phase deliverables precisely (backend + frontend as applicable).
2) Update OpenAPI + deterministic SDK generation outputs if endpoints/types change.
3) Add/adjust tests so verification commands are green.

DELIVERABLES
- Concrete code changes
- Updated OpenAPI + SDK artifacts when required
- Passing verification commands
```

## Verification Commands

```text
cd apps/api && uv run pytest -q
pnpm -r typecheck
pnpm -r build
pnpm run openapi:generate
pnpm run sdk:check
```

## Acceptance Checks

- Phase 55 deliverables are implemented.
- All verification commands pass (green).
- No new monolithic files created; any touched file >400 lines must be split as part of the phase.

### Phase-specific requirements
Compliance
- Evidence bundle generator for an episode:
  - compile timeline + evidence metadata + audit trail into a bundle artifact (zip/pdf later; zip ok now).
- Scheduled reports:
  - model ReportJob (tenant-scoped), generate on schedule, store artifact reference.
- Submission tracking:
  - model SubmissionRecord with due_date/submitted_at/status.

Frontend
- Episode -> Compliance tab with 'Generate bundle' and list of bundles.
