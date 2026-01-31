# 00_RULES_AND_GATES

## Cursor Agent Prompt
```text
Create a CareOS monorepo baseline and enforce Cursor rules first.

1) Ensure .cursor/rules/*.mdc exists exactly as provided in this repository.
2) Implement repo-level guardrails to prevent low quality:
   - Add a repository script that fails if any TODO/FIXME/placeholder/stub is introduced anywhere under apps/ packages/ infra/
   - Add a script that fails if secrets-like patterns are detected (basic high-signal checks)
3) Add a root Makefile (or task runner) exposing:
   - make lint
   - make typecheck
   - make test
   - make build
   - make verify (runs all)
4) Ensure these commands are used in CI later.

Do not create application logic in this milestone.

```

## Verification Commands
```text
make verify
git status
find . -path './.git/*' -prune -o -type f -name '*.mdc' -print

```

## Acceptance Checks
- The rules bundle exists under .cursor/rules/ with no empty files.
- make verify exists and runs locally.
- The repository contains a script that fails builds when TODO/FIXME/placeholder/stub appears.
- The repository contains a script that fails builds when obvious secret patterns appear.

