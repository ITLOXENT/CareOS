# 77_ACCESSIBILITY_I18N_AND_UX_POLISH

## Cursor Agent Prompt

```text
Implement accessibility (WCAG AA), i18n scaffolding (en-GB default), and consistent design tokens across apps.

Frontend:
- Establish shared design tokens (Tailwind config + CSS vars) and apply to web-admin and web-portal.
- Add i18n plumbing (messages file, locale switcher hidden behind flag).
- Accessibility: focus states, labels, keyboard navigation, contrast checks.

Verification:
- Run Lighthouse/a11y checks (where automated), ensure no blocking issues.
```

## Verification Commands

```text
pnpm -r build
pnpm -r typecheck
```

## Acceptance Checks

- Consistent styling across apps.
- i18n scaffolding in place.
- Basic a11y checks pass.
