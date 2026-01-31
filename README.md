CareOS Cursor Build Package

What this package contains

- .cursor/rules/\*.mdc : fully written Cursor Rules bundle tailored to CareOS
- docs/cursor/AGENT_MASTER_SCRIPT.md : milestone-by-milestone Cursor prompt script (exact files, commands, acceptance checks)
- docs/cursor/MILESTONES/\*.md : one file per milestone with prompts and verification commands
- docs/cursor/UPLOAD_INSTRUCTIONS.md : how to install this package into your repo and how Cursor uses the rules

How to use (fast)

1. Unzip this package into the root of your repo (or a new repo). It will create:
   - .cursor/rules/
   - docs/cursor/
2. Open the repo in Cursor.
3. Ensure Cursor Rules are enabled for the workspace.
4. Start in: docs/cursor/MILESTONES/00_RULES_AND_GATES.md
   Copy/paste the "Cursor Agent Prompt" block into Cursor Agent.

No placeholders policy

- The rules enforce: no TODOs, stubs, fake endpoints, non-functional routes, or silent fallbacks.
- If an external integration is not available in MVP, the rules require a production-safe simulator with the same interface and full audit trail.

Framework baselines (pin these; upgrade promptly for security)

- Backend: Django 6.0.1 (release notes: 2026-01-06)
- Web: Next.js 16.1 (blog: 2025-12-18)
- Mobile: React Native 0.83 (blog: 2025-12-10)
- Database: PostgreSQL 18 (released 2025-09-25)

You can change pins, but keep the same quality/security guardrails.

Developer commands (local)

1. Install JS dependencies
   - pnpm install
2. Install Python dependencies (apps/api)
   - uv pip install -r apps/api/requirements.txt -r apps/api/requirements-dev.txt
   - python -m pip install -r apps/api/requirements.txt -r apps/api/requirements-dev.txt
3. Run JS checks
   - pnpm -r lint
   - pnpm -r typecheck
   - pnpm -r test --if-present
   - pnpm -r build --if-present
   - pnpm exec prettier --check .
4. Run Python checks
   - cd apps/api && python -m ruff check .
   - cd apps/api && python -m ruff format --check .
   - cd apps/api && python -m mypy .
   - cd apps/api && python -m pytest -q
   - cd apps/api && python -m pip_audit -r requirements.txt -r requirements-dev.txt
5. Guardrails
   - python scripts/guardrails/check_no_placeholders.py
   - python scripts/guardrails/check_no_secrets.py
   - python scripts/guardrails/check_iac.py
6. All checks
   - make verify
7. Pre-commit hooks
   - pre-commit install
   - pre-commit run --all-files
