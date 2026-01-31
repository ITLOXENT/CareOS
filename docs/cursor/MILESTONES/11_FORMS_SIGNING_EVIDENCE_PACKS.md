# 11_FORMS_SIGNING_EVIDENCE_PACKS

## Cursor Agent Prompt

```text
Implement forms, signing, and evidence pack generation.

Backend:
- FormTemplate (versioned)
- FormResponse (validated)
- Signature model (who/when/template version)
- EvidencePack generator:
  - JSON manifest with referenced EpisodeEvents and Signatures
  - PDF export
- Endpoints:
  - GET /forms/templates
  - POST /forms/responses
  - POST /forms/responses/{id}/sign
  - POST /episodes/{id}/evidence-pack/generate
  - GET /evidence-packs/{id}

Frontend:
- Fill a form on an episode and sign it
- Generate and download evidence pack

Tests:
- Evidence pack determinism
- Hash chain verification

```

## Verification Commands

```text
cd apps/api && uv run pytest -q
pnpm -r build

```

## Acceptance Checks

- Evidence pack includes event IDs, hashes, signatures.
- Evidence pack generation is deterministic in tests.
- Evidence pack is downloadable from admin UI.
