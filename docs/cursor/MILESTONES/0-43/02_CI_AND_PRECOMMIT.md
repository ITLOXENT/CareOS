# 02_CI_AND_PRECOMMIT

## Cursor Agent Prompt

```text
Implement CI and pre-commit hooks that enforce quality gates.

CI requirements:
- Lint: Python ruff + TS eslint
- Format check: ruff format + prettier
- Typecheck: mypy + tsc
- Tests: pytest + minimal JS tests where applicable
- Dependency audit: pip-audit + pnpm audit
- Secret scan: at least a basic scanner
- IaC checks: terraform fmt/validate + tflint/tfsec if available

Pre-commit:
- Provide a pre-commit config or package scripts that run the same checks.

Update root README with exact developer commands.

```

## Verification Commands

```text
pnpm -r lint
pnpm -r typecheck
pnpm -r test || true
pnpm -r build
cd apps/api && uv run ruff check . && uv run ruff format --check .
cd apps/api && uv run mypy .
cd apps/api && uv run pytest -q

```

## Acceptance Checks

- .github/workflows contains CI that runs on pull_request.
- CI fails if lint/typecheck/tests fail.
- Pre-commit equivalent exists and is documented.
- Running make verify passes locally.
