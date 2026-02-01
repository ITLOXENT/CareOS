# 56_WEB_ADMIN_UX_POLISH

## Cursor Agent Prompt

```text
Web-admin UX polish: pagination, filtering, optimistic UI, error states, accessibility pass.

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

- Phase 56 deliverables are implemented.
- All verification commands pass (green).
- No new monolithic files created; any touched file >400 lines must be split as part of the phase.

### Phase-specific requirements
Web-admin
- Pagination and stable filtering for Inbox/Episodes/Notifications/Evidence.
- Empty/loading/error states.
- Basic accessibility pass: focus states, keyboard nav, headings, labels.
- Remove any overgrown page components by splitting into smaller components.
