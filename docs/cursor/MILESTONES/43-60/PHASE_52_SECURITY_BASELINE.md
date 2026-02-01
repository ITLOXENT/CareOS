# 52_SECURITY_BASELINE

## Cursor Agent Prompt

```text
Security baseline: MFA (staff), password/session policies, headers, rate limits, secrets handling.

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

- Phase 52 deliverables are implemented.
- All verification commands pass (green).
- No new monolithic files created; any touched file >400 lines must be split as part of the phase.

### Phase-specific requirements
Security
- MFA for staff (TOTP) end-to-end for web-admin login.
- Strong session/cookie settings: HttpOnly, Secure, SameSite, rotation, idle timeout.
- Password policy enforcement (length, rate limiting).
- Security headers (CSP, HSTS, X-Frame-Options, etc.) appropriate for Next + Django.
- Add rate limiting for auth endpoints.
- Secrets: ensure no secrets committed; document required env vars.

Tests
- MFA required for staff access to protected routes.
