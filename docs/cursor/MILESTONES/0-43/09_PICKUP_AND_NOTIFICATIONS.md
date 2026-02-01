# 09_PICKUP_AND_NOTIFICATIONS

## Cursor Agent Prompt

```text
Implement pickup readiness + notifications with outbox pattern.

Backend:
- PickupStatus on Episode or a dedicated Pickup model
- NotificationOutbox with statuses and retries
- Providers:
  - Email provider (dev can log-only but must be implemented as provider with interface)
  - SMS provider (same)
  - Push provider (same)
- Endpoints:
  - POST /episodes/{id}/pickup/status
  - POST /episodes/{id}/notify/pickup-ready
  - GET /notifications

Frontend:
- Episode detail includes pickup status and notify action
- Notification log view

Mobile:
- Basic push receive and display pickup update

Tests:
- Outbox retry behavior
- No sensitive data in push payload

```

## Verification Commands

```text
cd apps/api && uv run pytest -q
pnpm -r build

```

## Acceptance Checks

- Marking an episode "ready" triggers notification via outbox worker.
- Notification delivery status updates are visible in admin.
- Mobile receives push and then fetches details via authenticated API.
