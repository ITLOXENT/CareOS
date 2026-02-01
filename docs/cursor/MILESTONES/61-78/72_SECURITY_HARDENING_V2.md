# 72_SECURITY_HARDENING_V2

## Cursor Agent Prompt

```text
Security hardening v2 across backend and frontends.

Backend:
- Add CSP headers, secure cookies defaults, CSRF protection for session endpoints, strict CORS.
- Rate limit auth endpoints and key write endpoints.
- Password policy + MFA enforcement rules (per-tenant policy).
- Secrets handling: ensure no secrets in repo; document env vars; add startup validation.

Frontend:
- Ensure no sensitive data in logs; sanitize error surfaces.

Tests:
- Security regression tests (headers present, rate limit on).
```

## Verification Commands

```text
cd apps/api && uv run pytest -q
pnpm -r build
pnpm -r typecheck
```

## Acceptance Checks

- Security headers present.
- Auth endpoints rate-limited.
- MFA policy enforced.
- No secrets committed.
