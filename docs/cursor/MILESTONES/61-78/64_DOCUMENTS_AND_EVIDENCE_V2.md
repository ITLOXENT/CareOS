# 64_DOCUMENTS_AND_EVIDENCE_V2

## Cursor Agent Prompt

```text
Implement secure document storage, evidence capture, and attachment linking across Episodes (Documents & Evidence V2).

Backend:
- Add Document model improvements: content_type, sha256, size_bytes, storage_key, uploaded_by, malware_scan_status.
- Endpoints:
  - POST /documents/upload (pre-signed upload flow or direct upload MVP)
  - GET /documents/{id} (metadata)
  - GET /documents/{id}/download (signed URL)
  - POST /episodes/{id}/attachments (link existing document to episode)
- Add background job interface for malware scanning (stub) and block download if status=blocked.
- Ensure audit trail for upload/link/download.

Frontend:
- web-admin Evidence page: list documents + upload + link to episode.
- Episode detail: evidence tab with linked documents.

Tests:
- Download blocked when malware_scan_status=blocked.
- Tenant isolation for documents.
```

## Verification Commands

```text
cd apps/api && uv run pytest -q
pnpm -r build
pnpm -r typecheck
```

## Acceptance Checks

- Upload + link document to episode works end-to-end.
- Blocked documents cannot be downloaded.
- Audit log created for upload/link actions.
