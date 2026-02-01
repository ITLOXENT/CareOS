# PHASE 27 — Security hardening

## Cursor Agent Prompt

```text
Security hardening milestone for pilot readiness.

Backend:
- MFA (TOTP) optional per org policy OR mandatory for staff if feasible now.
- Session management: list sessions + revoke.
- Rate limit auth endpoints.
- Password policy + lockout throttling.
- Security headers for web apps.
- Audit logging for all auth events.

Frontend (web-admin):
- Account security page (MFA setup + sessions list).

Tests:
- MFA flow tests (if enabled)
- session revoke
- basic rate limiting
Docs:
- docs/security.md describing controls
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
- Staff auth hardened (MFA/policy-ready).
- Auth endpoints rate-limited.
- Sessions revocable.
- Audit events exist for auth/security actions.

## Suggested Commit Message
`Phase 27: security hardening`
