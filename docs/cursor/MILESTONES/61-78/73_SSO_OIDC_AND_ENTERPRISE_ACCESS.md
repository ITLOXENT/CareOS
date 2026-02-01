# 73_SSO_OIDC_AND_ENTERPRISE_ACCESS

## Cursor Agent Prompt

```text
Add OIDC SSO for enterprise tenants (staff portal + admin), including JIT provisioning and group-to-role mapping.

Backend:
- OIDC config per tenant: issuer, client_id, client_secret, redirect URIs.
- Implement OIDC login flow endpoints and callback.
- JIT: create user + membership on first login based on email domain and/or group mapping.
- Ensure MFA and session policies apply.

Frontend:
- web-admin login offers SSO button when tenant configured.
- web-portal staff login offers SSO.

Tests:
- OIDC flow unit tests using mocked provider.
```

## Verification Commands

```text
cd apps/api && uv run pytest -q
pnpm -r build
```

## Acceptance Checks

- SSO works for configured tenant.
- Users provisioned with correct roles.
- Server-side policies enforced.
