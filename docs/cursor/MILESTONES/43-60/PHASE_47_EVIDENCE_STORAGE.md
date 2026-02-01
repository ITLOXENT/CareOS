# 47_EVIDENCE_STORAGE

## Cursor Agent Prompt

```text
Evidence storage end-to-end (upload, metadata, access control, retention hooks).

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

- Phase 47 deliverables are implemented.
- All verification commands pass (green).
- No new monolithic files created; any touched file >400 lines must be split as part of the phase.

### Phase-specific requirements
Backend
- EvidenceItem model (tenant-scoped), linked to Episode.
- Upload flow (choose one):
  A) Local dev: store in filesystem + reference path
  B) Production: S3-compatible signed URL flow (recommended)
- Endpoints:
  - POST /episodes/{id}/evidence (create metadata + upload initiation)
  - GET /episodes/{id}/evidence
  - GET /evidence/{id} (authorized access)
- Access control: only members of org with permission can view/download.
- Retention hooks: store retention_class + retention_until; enforce later.

Frontend (web-admin)
- Evidence tab on episode: list, upload, download/view.
