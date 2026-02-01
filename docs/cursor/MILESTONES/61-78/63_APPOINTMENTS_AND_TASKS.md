# 63_APPOINTMENTS_AND_TASKS

## Cursor Agent Prompt

```text
Implement appointments + task orchestration with reminders and SLA, integrated with Episodes/WorkItems.

Backend:
- Models: Appointment (patient optional, episode optional, scheduled_at, duration, location, status), Task (episode/work_item link, due_at, priority, status).
- State transitions for Appointment and Task (explicit allowed transitions).
- Endpoints:
  - POST/GET /appointments
  - POST /appointments/{id}/transition
  - GET/POST /tasks
  - POST /tasks/{id}/assign
  - POST /tasks/{id}/complete
- Integrate with WorkItem: creating an Episode or Appointment can auto-create a WorkItem (configurable flag).

Frontend (web-admin):
- Inbox: new filters for due_at/SLA and appointment linkage.
- Episode detail: show linked appointments and tasks.

Tests:
- Transition validation tests.
- SLA filter correctness.
```

## Verification Commands

```text
cd apps/api && uv run pytest -q
pnpm -r build
pnpm -r typecheck
```

## Acceptance Checks

- Staff can create appointments/tasks, assign, complete.
- Work Inbox reflects tasks with filters.
- Every transition appends EpisodeEvent/AuditEvent where relevant.
