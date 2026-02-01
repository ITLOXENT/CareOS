# PHASE 22 — web-portal auth + consent shell

## Cursor Agent Prompt

```text
Implement web-portal authentication shell (patients/caregivers).

Backend:
- PortalInvite model (org + patient + email/phone + role PATIENT/CAREGIVER; signed token + expiry).
- Endpoints:
  - POST /portal/auth/accept-invite
  - POST /portal/auth/login (choose OTP or passwordless method)
  - GET /portal/me

Frontend (web-portal):
- Login page
- Protected layout
- Profile page showing /portal/me

Security:
- Portal endpoints isolated from staff endpoints.
- Tenant scoping by invite + session.

Tests:
- invite acceptance
- tenant isolation
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
- Portal user can login and hit /portal/me.
- Portal cannot access staff-only endpoints/data.
- Tenant isolation tests pass.

## Suggested Commit Message
`Phase 22: portal auth shell`
