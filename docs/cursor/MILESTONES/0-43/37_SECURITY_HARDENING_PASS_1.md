# Phase 37 — SECURITY_HARDENING_PASS_1

## Cursor Agent Prompt
```text
Security hardening pass 1 across API and web-admin/web-portal.

Backend:
- Ensure auth cookies are HttpOnly, Secure in prod, SameSite=Lax/Strict as appropriate.
- Add rate-limiting minimal middleware (in-memory) for login endpoint.
- Ensure logging redaction covers: passwords, tokens, cookies, auth headers, PII fields already identified.
- Add explicit `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` per environment.

Frontend:
- Ensure login flow does not expose secrets in logs.
- Ensure API base URL is environment-driven and not hardcoded.
```

## Verification Commands
```text
cd apps/api
uv run pytest -q
pnpm -r typecheck
pnpm -r build
```

## Acceptance Checks
- Existing tests still pass.
- Cookies and security flags set correctly per environment config.
- No secrets printed in console during normal flows.


