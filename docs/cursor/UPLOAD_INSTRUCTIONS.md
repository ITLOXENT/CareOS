How to install this package into your project

Option A (recommended): Start a new repo

1. Create a new empty git repo (e.g., careos).
2. Unzip this package into the repo root.
3. Open the folder in Cursor.
4. Begin executing milestones from docs/cursor/MILESTONES/00_RULES_AND_GATES.md

Option B: Add to an existing repo

1. Unzip this package into the existing repo root.
2. If asked to overwrite existing files:
   - Keep your existing app code
   - Always keep .cursor/rules/\*.mdc from this package (these are the guardrails)
   - Merge docs/ content as needed
3. Open the repo in Cursor and begin executing milestones.

Where Cursor reads rules from
Cursor supports project rules located under:

- .cursor/rules/\*.mdc

These rules are automatically applied by Cursor when rules are enabled for the workspace.
If you also use user-level rules, keep them compatible with this repo’s rules.

How to run the plan

- Open docs/cursor/AGENT_MASTER_SCRIPT.md
- Run milestones in order (00 → 12)
- Do not skip Milestone 00 and 01. They set up the gates that prevent low-quality code.

Outputs you should always expect per milestone

- Exact file diffs
- Exact verification commands
- Passing results for: lint, typecheck, tests, build
- Updated documentation and evidence artifacts where required
