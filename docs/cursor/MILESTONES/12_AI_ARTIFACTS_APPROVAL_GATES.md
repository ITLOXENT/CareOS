# 12_AI_ARTIFACTS_APPROVAL_GATES

## Cursor Agent Prompt
```text
Implement AI artifacts with approval gates.

Backend:
- AIArtifact model with versioning, confidence, policy version, approvals
- Endpoints:
  - POST /ai/triage/suggest
  - POST /ai/note/draft
  - POST /ai/completeness/check
  - POST /ai/{id}/approve
  - POST /ai/{id}/reject
- Hard rules enforced by code:
  - AI outputs cannot transition episode state or be exported without approval
- Redaction layer for AI prompts

Frontend:
- AI Review queue
- Approve/reject with audit trail

Tests:
- Approval required tests
- Audit events for approvals

```

## Verification Commands
```text
cd apps/api && uv run pytest -q
pnpm -r build

```

## Acceptance Checks
- AI suggestions appear as artifacts pending review.
- Approvals are recorded and audited.
- System blocks any attempt to use unapproved artifacts.

