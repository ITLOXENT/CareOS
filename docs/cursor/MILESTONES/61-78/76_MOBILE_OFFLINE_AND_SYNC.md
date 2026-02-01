# 76_MOBILE_OFFLINE_AND_SYNC

## Cursor Agent Prompt

```text
Add offline-first cache + sync for mobile.

Mobile:
- Local storage for Patient list/detail, notifications, and assigned work items.
- Sync engine: periodic refresh, manual refresh, conflict handling (server wins for MVP).
- Connectivity indicator + graceful error UI.

Backend:
- Ensure list endpoints support updated_since cursor to reduce payload size.

Tests:
- Mobile unit tests for sync logic (where applicable).
```

## Verification Commands

```text
pnpm -r build
pnpm -r typecheck
cd apps/api && uv run pytest -q
```

## Acceptance Checks

- Mobile works offline for core read flows.
- Sync refreshes data when back online.
- Backend supports updated_since cursors.
