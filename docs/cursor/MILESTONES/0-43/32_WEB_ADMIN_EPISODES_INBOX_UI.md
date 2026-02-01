# Phase 32 — WEB_ADMIN_EPISODES_INBOX_UI

## Cursor Agent Prompt
```text
Implement real Episodes + Inbox UI in web-admin (no placeholders).

Frontend (apps/web-admin):
- Inbox page:
  - Calls GET /work-items via packages/sdk
  - Filters: status(open/assigned/done), assignee(me/unassigned/all), SLA(overdue/next 24h/all)
  - Table rows link to Episode detail
- Episodes list page:
  - Calls GET /episodes via packages/sdk
  - Basic search by title
- Create episode flow:
  - Form: title, description
  - Calls POST /episodes
  - Redirect to episode detail
- Episode detail page:
  - Calls GET /episodes/{id}
  - Calls GET /episodes/{id}/timeline
  - Transition dropdown/buttons based on allowed transitions returned by server (preferred) or derived from status and role
  - Calls POST /episodes/{id}/transition then refreshes
- Ensure all API calls use packages/sdk only.
- Route guard remains in place.
```

## Verification Commands
```text
pnpm -r typecheck
pnpm -r build
```

## Acceptance Checks
- Staff can create an episode from web-admin.
- Staff can see it in Inbox and navigate to detail.
- Transitions work and timeline updates immediately.
- No direct fetch to API; only `@careos/sdk` usage.


