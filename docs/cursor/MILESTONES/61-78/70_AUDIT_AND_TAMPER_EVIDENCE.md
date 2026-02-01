# 70_AUDIT_AND_TAMPER_EVIDENCE

## Cursor Agent Prompt

```text
Harden AuditEvent to be tamper-evident (hash chaining), add export endpoints, and retention/immutability controls.

Backend:
- Add fields: prev_hash, event_hash, chain_id; compute event_hash over canonical JSON.
- Enforce append-only at DB/service layer.
- Endpoints:
  - GET /audit/events (filtered, paginated)
  - GET /audit/events/export (CSV/JSON)
  - GET /audit/chain/verify (verify hashes for a range)
- Retention policy model with legal holds.

Tests:
- Hash chain verification test ensures tamper detection.
```

## Verification Commands

```text
cd apps/api && uv run pytest -q
```

## Acceptance Checks

- Audit logs are tamper-evident.
- Export works and respects RBAC.
- Verification endpoint detects corruption.
