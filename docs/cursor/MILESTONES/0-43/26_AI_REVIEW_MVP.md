# PHASE 26 — AI Review MVP

## Cursor Agent Prompt

```text
Implement AI Review MVP (assistive only, auditable, safe).

Backend:
- AIReviewRequest model (tenant-scoped): input_type, payload, status, output, created_by/created_at, model/version metadata.
- Endpoints:
  - POST /ai/review
  - GET /ai/review/{id}
- Worker executes AI calls; tests use mocked provider.
- Audit events for request creation and completion.
- Never auto-transition episodes based on AI.

Frontend (web-admin):
- AI Review page lists requests and results.
- Episode detail: “Generate summary” button.

Tests:
- RBAC, tenancy, mocked provider
```

## Verification Commands

```text
pnpm run openapi:generate
pnpm run sdk:check
pnpm -r typecheck
pnpm -r build
cd apps/api && uv run pytest -q
```

## Acceptance Checks
- Staff can request AI summary and view result.
- No automatic workflow changes.
- Processing is asynchronous and auditable.
- Tests use mocked provider only.

## Suggested Commit Message
`Phase 26: ai review mvp`
