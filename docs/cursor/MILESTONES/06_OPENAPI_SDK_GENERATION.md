# 06_OPENAPI_SDK_GENERATION

## Cursor Agent Prompt

```text
Add OpenAPI generation in apps/api and typed SDK generation into packages/sdk and packages/types.

Requirements:
- API schema must be deterministic and checked into the repo or generated in CI.
- SDK generation command must run from repo root.
- web-admin and web-portal must call API through packages/sdk only.

Add acceptance tests:
- SDK generation produces consistent output.
- Typecheck fails if API contract mismatch occurs.

Update docs/architecture/contracts.md describing the contract workflow.

```

## Verification Commands

```text
pnpm -r typecheck
cd apps/api && uv run pytest -q

```

## Acceptance Checks

- packages/sdk contains a generated client.
- web-admin and web-portal import from packages/sdk.
- CI includes a job that regenerates schema and fails if drift is detected.
