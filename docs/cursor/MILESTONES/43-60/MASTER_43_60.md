# CareOS Phase Pack 43–60

Generated: 2026-02-01

This pack continues after Phase 42. Each phase includes a Cursor Agent Prompt, verification commands, and acceptance checks.

## Quick start (local dev)

```bash
# backend
cd apps/api && DJANGO_SETTINGS_MODULE=careos_api.settings.dev uv run python manage.py migrate && uv run python manage.py runserver

# web-admin
cd apps/web-admin && pnpm dev

# web-portal
cd apps/web-portal && pnpm dev
```

- [PHASE_43_DB_MIGRATIONS_EPISODES_INBOX.md](./PHASE_43_DB_MIGRATIONS_EPISODES_INBOX.md) — Fix Episode/WorkItem migrations + pytest DB setup (green tests).
- [PHASE_44_API_REFACTOR_MODELS.md](./PHASE_44_API_REFACTOR_MODELS.md) — Split monolithic core/models.py into domain modules (episodes, inbox, evidence, audit, orgs).
- [PHASE_45_API_REFACTOR_VIEWS_URLS.md](./PHASE_45_API_REFACTOR_VIEWS_URLS.md) — Split monolithic core/views.py into domain view modules + explicit urls.py routing.
- [PHASE_46_EPISODES_INBOX_COMPLETE.md](./PHASE_46_EPISODES_INBOX_COMPLETE.md) — Complete Episodes + Work Inbox endpoints, transitions, timeline, and tenant isolation.
- [PHASE_47_EVIDENCE_STORAGE.md](./PHASE_47_EVIDENCE_STORAGE.md) — Evidence storage end-to-end (upload, metadata, access control, retention hooks).
- [PHASE_48_NOTIFICATIONS_ENGINE.md](./PHASE_48_NOTIFICATIONS_ENGINE.md) — Notifications engine (in-app) + delivery wiring stubs + web-admin UI.
- [PHASE_49_AUDIT_HARDENING.md](./PHASE_49_AUDIT_HARDENING.md) — Audit coverage hardening for all sensitive actions + middleware + exports.
- [PHASE_50_BILLING_ENTITLEMENTS.md](./PHASE_50_BILLING_ENTITLEMENTS.md) — Stripe billing (UK/US-ready) + entitlements/feature flags + org subscription state.
- [PHASE_51_ADMIN_SETTINGS_REAL.md](./PHASE_51_ADMIN_SETTINGS_REAL.md) — Admin Settings: staff/user management, roles, org config, API keys, integration toggles.
- [PHASE_52_SECURITY_BASELINE.md](./PHASE_52_SECURITY_BASELINE.md) — Security baseline: MFA (staff), password/session policies, headers, rate limits, secrets handling.
- [PHASE_53_PRIVACY_GDPR_DSAR.md](./PHASE_53_PRIVACY_GDPR_DSAR.md) — GDPR/Privacy: consent records, DSAR export/delete, retention policies, audit evidence.
- [PHASE_54_OBSERVABILITY.md](./PHASE_54_OBSERVABILITY.md) — Observability: structured logs, metrics, tracing hooks, error reporting (Sentry-ready).
- [PHASE_55_COMPLIANCE_REPORTING.md](./PHASE_55_COMPLIANCE_REPORTING.md) — Compliance reporting: evidence bundles, scheduled reports, exports, submission tracking.
- [PHASE_56_WEB_ADMIN_UX_POLISH.md](./PHASE_56_WEB_ADMIN_UX_POLISH.md) — Web-admin UX polish: pagination, filtering, optimistic UI, error states, accessibility pass.
- [PHASE_57_WEB_PORTAL_MINIMUM.md](./PHASE_57_WEB_PORTAL_MINIMUM.md) — Web-portal minimum: auth, user profile, view episodes, notifications.
- [PHASE_58_MOBILE_MINIMUM.md](./PHASE_58_MOBILE_MINIMUM.md) — Mobile minimum: auth shell, inbox/notifications read-only, deep links.
- [PHASE_59_RELEASE_RUNBOOK.md](./PHASE_59_RELEASE_RUNBOOK.md) — Release readiness: runbooks, backup/restore checks, DR checklist, env matrix, operational docs.
- [PHASE_60_SECURITY_REVIEW_GATE.md](./PHASE_60_SECURITY_REVIEW_GATE.md) — Security/compliance review gate: threat model, pen-test checklist, policy mapping, final sign-off.
