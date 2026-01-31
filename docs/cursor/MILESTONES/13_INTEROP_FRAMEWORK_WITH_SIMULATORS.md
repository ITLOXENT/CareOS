# 13_INTEROP_FRAMEWORK_WITH_SIMULATORS

## Cursor Agent Prompt
```text
Implement integration framework with production-safe simulators.

Backend:
- InteropMessage model + outbox processing
- Adapter interfaces for NHS and US integrations
- Simulator implementations that:
  - mimic real lifecycles
  - record audit and status updates
  - require explicit config enablement
- Admin UI to view message lifecycles

Tests:
- Message lifecycle tests
- Simulator determinism tests

```

## Verification Commands
```text
cd apps/api && uv run pytest -q
pnpm -r build

```

## Acceptance Checks
- Interop messages can be drafted, queued, processed, and reach final status in simulator mode.
- Every step is audited.
- Simulator mode is disabled by default in production config.

