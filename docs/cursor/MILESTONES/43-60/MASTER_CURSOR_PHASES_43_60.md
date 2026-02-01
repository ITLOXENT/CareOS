# MASTER_CURSOR_PHASES_43_60
Generated: 2026-02-01

Apply phases in order. After each phase, run verification commands and commit with a clear message.


## Phase 43: DB_MIGRATIONS_EPISODES_INBOX
Fix Episode/WorkItem migrations + pytest DB setup (green tests).

See: PHASE_43_DB_MIGRATIONS_EPISODES_INBOX.md


## Phase 44: API_REFACTOR_MODELS
Split monolithic core/models.py into domain modules (episodes, inbox, evidence, audit, orgs).

See: PHASE_44_API_REFACTOR_MODELS.md


## Phase 45: API_REFACTOR_VIEWS_URLS
Split monolithic core/views.py into domain view modules + explicit urls.py routing.

See: PHASE_45_API_REFACTOR_VIEWS_URLS.md


## Phase 46: EPISODES_INBOX_COMPLETE
Complete Episodes + Work Inbox endpoints, transitions, timeline, and tenant isolation.

See: PHASE_46_EPISODES_INBOX_COMPLETE.md


## Phase 47: EVIDENCE_STORAGE
Evidence storage end-to-end (upload, metadata, access control, retention hooks).

See: PHASE_47_EVIDENCE_STORAGE.md


## Phase 48: NOTIFICATIONS_ENGINE
Notifications engine (in-app) + delivery wiring stubs + web-admin UI.

See: PHASE_48_NOTIFICATIONS_ENGINE.md


## Phase 49: AUDIT_HARDENING
Audit coverage hardening for all sensitive actions + middleware + exports.

See: PHASE_49_AUDIT_HARDENING.md


## Phase 50: BILLING_ENTITLEMENTS
Stripe billing (UK/US-ready) + entitlements/feature flags + org subscription state.

See: PHASE_50_BILLING_ENTITLEMENTS.md


## Phase 51: ADMIN_SETTINGS_REAL
Admin Settings: staff/user management, roles, org config, API keys, integration toggles.

See: PHASE_51_ADMIN_SETTINGS_REAL.md


## Phase 52: SECURITY_BASELINE
Security baseline: MFA (staff), password/session policies, headers, rate limits, secrets handling.

See: PHASE_52_SECURITY_BASELINE.md


## Phase 53: PRIVACY_GDPR_DSAR
GDPR/Privacy: consent records, DSAR export/delete, retention policies, audit evidence.

See: PHASE_53_PRIVACY_GDPR_DSAR.md


## Phase 54: OBSERVABILITY
Observability: structured logs, metrics, tracing hooks, error reporting (Sentry-ready).

See: PHASE_54_OBSERVABILITY.md


## Phase 55: COMPLIANCE_REPORTING
Compliance reporting: evidence bundles, scheduled reports, exports, submission tracking.

See: PHASE_55_COMPLIANCE_REPORTING.md


## Phase 56: WEB_ADMIN_UX_POLISH
Web-admin UX polish: pagination, filtering, optimistic UI, error states, accessibility pass.

See: PHASE_56_WEB_ADMIN_UX_POLISH.md


## Phase 57: WEB_PORTAL_MINIMUM
Web-portal minimum: auth, user profile, view episodes, notifications.

See: PHASE_57_WEB_PORTAL_MINIMUM.md


## Phase 58: MOBILE_MINIMUM
Mobile minimum: auth shell, inbox/notifications read-only, deep links.

See: PHASE_58_MOBILE_MINIMUM.md


## Phase 59: RELEASE_RUNBOOK
Release readiness: runbooks, backup/restore checks, DR checklist, env matrix, operational docs.

See: PHASE_59_RELEASE_RUNBOOK.md


## Phase 60: SECURITY_REVIEW_GATE
Security/compliance review gate: threat model, pen-test checklist, policy mapping, final sign-off.

See: PHASE_60_SECURITY_REVIEW_GATE.md
