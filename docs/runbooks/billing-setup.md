## Billing setup runbook

### Environment variables

- `STRIPE_SECRET_KEY`: Stripe secret key for API calls.
- `STRIPE_WEBHOOK_SECRET`: Stripe webhook signing secret.
- `STRIPE_PRICE_STARTER`: Price ID for the starter plan.
- `STRIPE_PRICE_PRO`: Price ID for the pro plan.
- `SLA_WARNING_MINUTES`: Optional, does not affect billing.

### Webhook endpoint

- Configure Stripe to send events to `POST /billing/webhook/`.
- Subscribe to:
  - `customer.subscription.updated`
  - `customer.subscription.deleted`
  - `invoice.paid`
  - `invoice.payment_failed`

### Plan configuration

- Edit `BILLING_PLANS` in `apps/api/careos_api/settings/base.py` to add or adjust plan codes and seat counts.
- Ensure `price_id` values match Stripe Price IDs.

### Verification

- Trigger a checkout via `POST /billing/checkout-session`.
- Confirm webhooks update `OrganizationSubscription` status and seat limits.
- Verify invite creation is blocked when seat limit is reached.
