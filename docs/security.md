## Security controls

### Authentication hardening

- Admin login enforces a minimum password length (12).
- MFA via TOTP for staff login if `ADMIN_TOTP_SECRET` is configured.
- Set `ADMIN_MFA_REQUIRED=true` in production to require MFA.
- Login endpoints are rate-limited and lock out after repeated failures.

### Sessions

- Admin sessions are tracked and can be revoked from Account Security.
- Sessions enforce an idle timeout (`ADMIN_SESSION_IDLE_SECONDS`).
- Revoked sessions are invalidated immediately for protected routes.

### Cookie & session policy

- HttpOnly cookies, SameSite=Lax, secure in production.
- Session expiry set to 8 hours with idle extension on activity.

### Rate limiting

- Portal and patient auth endpoints are rate-limited in the API.

### Security headers

- Web apps set `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`,
  `Permissions-Policy`, and `Content-Security-Policy`.

### Required security env vars

- `ADMIN_USERNAME`, `ADMIN_PASSWORD`
- `ADMIN_TOTP_SECRET` (MFA)
- `ADMIN_MFA_REQUIRED` (true/false)
- `ADMIN_SESSION_SECRET`
- `ADMIN_SESSION_IDLE_SECONDS`

### Audit logging

- Portal login and invite acceptance emit audit events.
- Patient OTP request/verify emit audit events.
