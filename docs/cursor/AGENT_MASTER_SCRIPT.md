CareOS Cursor Agent Master Script

How to run this
- Execute milestones in order from docs/cursor/MILESTONES/
- For each milestone:
  - Paste the "Cursor Agent Prompt" block into Cursor Agent
  - Do not proceed until all verification commands and acceptance checks pass
- Do not skip Milestone 00 and 01. They prevent low-quality code.

Milestone index
00_RULES_AND_GATES
01_MONOREPO_SCAFFOLD
02_CI_AND_PRECOMMIT
03_INFRA_TERRAFORM_BASELINE
04_COMPLIANCE_PACK
05_API_KERNEL_TENANCY_RBAC_AUDIT
06_OPENAPI_SDK_GENERATION
07_WEB_ADMIN_SHELL
08_EPISODES_AND_INBOX
09_PICKUP_AND_NOTIFICATIONS
10_MOBILE_MVP_ADHERENCE
11_FORMS_SIGNING_EVIDENCE_PACKS
12_AI_ARTIFACTS_APPROVAL_GATES
13_INTEROP_FRAMEWORK_WITH_SIMULATORS
14_PROD_READINESS_AND_GO_LIVE

Global invariants (must hold after every milestone)
- Lint passes (python + ts)
- Typecheck passes (python + ts)
- Tests pass
- Builds succeed for api/web/mobile where applicable
- No TODOs or placeholders
- Docs updated when required

Primary verification commands (adjust only if tools differ)
- Python:
  - cd apps/api && uv run ruff check . && uv run ruff format --check .
  - cd apps/api && uv run mypy .
  - cd apps/api && uv run pytest -q
- Node (from repo root):
  - pnpm -r lint
  - pnpm -r typecheck
  - pnpm -r test
  - pnpm -r build
- Terraform:
  - cd infra/terraform && terraform fmt -recursive && terraform validate

If you change tooling (poetry instead of uv, etc.), update milestone scripts accordingly.
