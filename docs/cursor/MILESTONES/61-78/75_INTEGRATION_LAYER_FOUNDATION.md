# 75_INTEGRATION_LAYER_FOUNDATION

## Cursor Agent Prompt

```text
Create integrations framework foundation: connector registry, webhook signing, outbound jobs, and sandbox mocks.

Backend:
- Models: IntegrationConnector, IntegrationCredential, WebhookSubscription, OutboundJob.
- Connector interface: validate(), pull(), push(), healthcheck().
- Add sandbox connectors (no real NHS integration yet):
  - FHIR sandbox (read/write Patient, Observation)
- Endpoints:
  - GET/POST /integrations/connectors
  - POST /integrations/{id}/test
  - POST /webhooks/{provider} (signed verification)

Frontend:
- web-admin Admin Settings: Integrations tab (list, configure, test).

Tests:
- Webhook signature verification test.
```

## Verification Commands

```text
cd apps/api && uv run pytest -q
pnpm -r build
```

## Acceptance Checks

- Integration framework can register/test connectors.
- Webhooks verify signatures.
- Admin UI can configure and run tests.
