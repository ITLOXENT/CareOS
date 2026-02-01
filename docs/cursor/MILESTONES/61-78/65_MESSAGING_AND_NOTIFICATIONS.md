# 65_MESSAGING_AND_NOTIFICATIONS

## Cursor Agent Prompt

```text
Implement secure internal messaging + notification delivery channels with opt-in preferences and audit logging.

Backend:
- Models: Conversation, Message, Notification, NotificationPreference (per-user, per-channel).
- Endpoints:
  - POST/GET /conversations
  - GET /conversations/{id}/messages
  - POST /conversations/{id}/messages
  - GET /notifications
  - POST /notifications/{id}/ack
  - GET/PATCH /me/notification-preferences
- Notification fan-out: on EpisodeEvent create a notification to assigned staff (MVP).

Frontend:
- web-admin Notifications page: list + ack.
- web-admin Inbox/Episode: quick link to conversation.
- web-portal: notifications list (read-only MVP).
- mobile: notifications list (read-only MVP).

Tests:
- RBAC: only members can read their notifications.
```

## Verification Commands

```text
cd apps/api && uv run pytest -q
pnpm -r build
pnpm -r typecheck
```

## Acceptance Checks

- Messages can be sent/read within tenant.
- Notifications appear for key events.
- Preferences can disable channels (still record audit).
