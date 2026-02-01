# PHASE 24 — SaaS billing subscriptions

## Cursor Agent Prompt

```text
Implement org subscription billing (Stripe).

Backend:
- OrganizationSubscription model: org, stripe ids, plan_code, status, current_period_end, seat limits.
- Endpoints:
  - GET /billing/plans
  - POST /billing/checkout-session
  - GET /billing/subscription
- Stripe webhooks: subscription updated/canceled; invoice paid/failed.
- ADMIN only.

Frontend (web-admin):
- Admin Settings -> Billing: show status, manage/upgrade.

Tests:
- webhook signature verification
- status transitions
- tenant isolation

Docs:
- billing setup runbook
```

## Verification Commands

```text
pnpm run openapi:generate
pnpm run sdk:check
pnpm -r typecheck
pnpm -r build
cd apps/api && uv run pytest -q
```

## Acceptance Checks
- Org admin can start checkout; subscription state is stored and updated by webhooks.
- Seat limit is enforced for invites/provisioning (at least MVP).
- Tests cover webhook + transitions.

## Suggested Commit Message
`Phase 24: billing subscriptions`
