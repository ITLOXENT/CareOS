# 07_WEB_ADMIN_SHELL

## Cursor Agent Prompt
```text
Implement web-admin staff dashboard shell with secure auth and RBAC-aware navigation.

Implement in apps/web-admin:
- Auth flow (MVP): staff login + session management
- Org switcher (if user has multiple org memberships)
- Basic layout with navigation:
  - Inbox
  - Episodes
  - Notifications
  - Evidence
  - AI Review
  - Admin Settings
- Route guards that hide unauthorized routes (server remains authoritative)

No business workflows yet beyond listing placeholder pages and wiring SDK calls to /me.

```

## Verification Commands
```text
pnpm -r build
pnpm -r typecheck

```

## Acceptance Checks
- Staff can login and see a dashboard.
- /me is called via packages/sdk.
- Unauthorized users cannot access protected routes.

