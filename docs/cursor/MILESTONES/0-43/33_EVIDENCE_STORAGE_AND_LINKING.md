# Phase 33 — EVIDENCE_STORAGE_AND_LINKING

## Cursor Agent Prompt
```text
Implement Evidence workflow (backend + minimal UI).

Backend:
- Evidence model (tenant-scoped):
  - organization, uploaded_by, filename, content_type, size_bytes, sha256, storage_key, created_at
- EpisodeEvidence link table:
  - episode, evidence, added_by, created_at
- Storage:
  - Local dev storage under `apps/api/.data/evidence/` with secure random filenames keyed by sha256 or UUID.
  - Provide abstraction to swap to S3 later (interface only, no AWS).
- Endpoints:
  - POST /evidence (multipart upload) -> returns evidence id + metadata
  - GET /evidence (list)
  - GET /episodes/{id}/evidence (list linked)
  - POST /episodes/{id}/evidence/{evidence_id} (link)
- RBAC:
  - Admin/Staff: upload and link
  - Viewer: list/read only
- Audit:
  - Upload and link operations create AuditEvents.

Frontend (web-admin):
- Episode detail adds an Evidence tab/section:
  - Upload file to POST /evidence, then link to episode
  - List linked evidence
```

## Verification Commands
```text
cd apps/api
uv run pytest -q
pnpm -r build
```

## Acceptance Checks
- Upload works in dev and evidence is stored on disk.
- Evidence can be linked to an episode.
- Tenant isolation + RBAC enforced.
- AuditEvents created for upload and link.


