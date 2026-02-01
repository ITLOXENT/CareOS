# 69_RBAC_POLICY_ENGINE_V2

## Cursor Agent Prompt

```text
Replace ad-hoc permission checks with a policy-driven RBAC engine (RBAC v2).

Backend:
- Define Permission and Policy tables (or static registry + DB overrides) to map:
  - route/action -> required permissions
  - role -> grants
  - org overrides
- Implement a central authorization function used by all views.
- Add endpoint:
  - GET /auth/policies (introspect current grants for logged-in user)
- Ensure existing endpoints (/episodes, /work-items, /patients, /documents, etc.) use the central policy check.

Frontend:
- web-admin nav + route guards consume /auth/policies and hide items accordingly.

Tests:
- Regression RBAC tests across key endpoints.
```

## Verification Commands

```text
cd apps/api && uv run pytest -q
pnpm -r build
pnpm -r typecheck
```

## Acceptance Checks

- Authorization is centralized and consistent.
- UI hides routes, server enforces access.
- RBAC tests cover multiple roles.
