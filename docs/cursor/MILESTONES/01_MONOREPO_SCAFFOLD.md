# 01_MONOREPO_SCAFFOLD

## Cursor Agent Prompt
```text
Scaffold the monorepo structure with pinned versions and deterministic tooling.

Create folders:
- apps/api
- apps/web-admin
- apps/web-portal
- apps/mobile
- packages/sdk
- packages/types
- infra/terraform
- docs/architecture
- docs/compliance

Tooling choices:
- Node: pnpm workspaces + turbo (optional but recommended)
- Python: uv preferred; alternatives allowed but must be deterministic and locked

Implement:
- root package.json workspace config
- root turbo.json (if used)
- Python project config for apps/api
- Next.js projects for web-admin and web-portal
- React Native project for mobile
- shared packages skeletons

Do not implement business features yet. Only scaffold runnable apps with hello pages and minimal endpoints.

```

## Verification Commands
```text
pnpm -v
pnpm -r lint || true
pnpm -r typecheck || true
pnpm -r build || true
cd apps/api && python -V

```

## Acceptance Checks
- apps/api can start (dev server) and serves a health endpoint.
- apps/web-admin builds and has a basic route.
- apps/web-portal builds and has a basic route.
- apps/mobile can compile at least one platform in CI (or local) with a default screen.
- No business logic beyond health/hello.

