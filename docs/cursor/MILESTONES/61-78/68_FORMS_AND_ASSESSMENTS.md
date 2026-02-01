# 68_FORMS_AND_ASSESSMENTS

## Cursor Agent Prompt

```text
Implement dynamic forms engine (templates + responses) with validation rules and auto-generated EpisodeEvents.

Backend:
- Models: FormTemplate, FormField, FormResponse, FormAnswer, ValidationRule (JSON logic).
- Endpoints:
  - POST/GET /forms/templates
  - GET/PATCH /forms/templates/{id}
  - POST /episodes/{id}/forms/{template_id}/submit
  - GET /episodes/{id}/forms
- Validation: server-side; invalid responses return structured errors.
- Submission creates EpisodeEvent + AuditEvent.

Frontend:
- web-admin: Episode detail includes "Forms" tab with render-from-schema + submit.
- mobile: render and submit 1 template type (MVP).

Tests:
- Validation rules enforced.
```

## Verification Commands

```text
cd apps/api && uv run pytest -q
pnpm -r build
pnpm -r typecheck
```

## Acceptance Checks

- Forms can be authored and submitted.
- Validation errors are clear.
- Episode timeline shows form submission events.
