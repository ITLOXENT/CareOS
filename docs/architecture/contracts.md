CareOS API Contract Workflow

Overview
CareOS maintains a deterministic OpenAPI schema checked into the repo and uses it
to generate typed SDK artifacts consumed by frontend apps.

Artifacts
- OpenAPI schema: `openapi.json`
- Generated types: `packages/types/src/openapi.ts`
- Generated SDK: `packages/sdk/src/generated.ts`

Generation commands (run from repo root)
1) Generate OpenAPI schema (uses uv + test settings)
   - pnpm run openapi:generate
   - underlying command:
     `cd apps/api && DJANGO_SETTINGS_MODULE=careos_api.settings.test uv run python manage.py generate_openapi --output ../../openapi.json`
2) Generate SDK artifacts
   - pnpm run sdk:generate
3) Check for drift (CI/pre-commit)
   - pnpm run sdk:check

Consumption rules
- Web apps (`apps/web-admin`, `apps/web-portal`) use `@careos/sdk` for API calls.
- Direct `fetch` calls to API endpoints should be avoided outside the SDK layer.
