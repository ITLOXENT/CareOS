# 10_MOBILE_MVP_ADHERENCE

## Cursor Agent Prompt

```text
Implement mobile MVP for adherence and caregiver.

Mobile:
- Medication schedule CRUD
- Local reminders
- Taken confirmation + missed dose tracking
- Caregiver invitation and permissioned alerts
- Feedback submission

Backend:
- Patient account auth (OTP)
- MedicationSchedule model (tenant-scoped to patient identity)
- Endpoints for schedule sync and feedback submission
- Feedback creates WorkItem in staff inbox

Tests:
- Reminder scheduling logic unit tests
- API integration tests for schedule sync

```

## Verification Commands

```text
pnpm -r build
pnpm -r typecheck
cd apps/api && uv run pytest -q

```

## Acceptance Checks

- Patient can set medication schedule and confirm doses.
- Missed dose creates an event and optional caregiver notification.
- Patient can submit feedback, and staff sees a work item in inbox.
