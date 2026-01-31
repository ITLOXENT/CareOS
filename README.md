CareOS Cursor Build Package

What this package contains
- .cursor/rules/*.mdc : fully written Cursor Rules bundle tailored to CareOS
- docs/cursor/AGENT_MASTER_SCRIPT.md : milestone-by-milestone Cursor prompt script (exact files, commands, acceptance checks)
- docs/cursor/MILESTONES/*.md : one file per milestone with prompts and verification commands
- docs/cursor/UPLOAD_INSTRUCTIONS.md : how to install this package into your repo and how Cursor uses the rules

How to use (fast)
1) Unzip this package into the root of your repo (or a new repo). It will create:
   - .cursor/rules/
   - docs/cursor/
2) Open the repo in Cursor.
3) Ensure Cursor Rules are enabled for the workspace.
4) Start in: docs/cursor/MILESTONES/00_RULES_AND_GATES.md
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
