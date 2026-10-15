# Task 045: Small UI polish

## Aim

Make Monitor feel more polished without adding complexity.

## Clarifications

- Keep the blue/teal identity; modest font, colour-shade and layout styling
  adjustments are welcome. Keep changes small and the app simple.

## Change

- Refine compact typography with one system sans-serif stack, consistent
  weights/spacing and aligned numeric values. No downloaded fonts.
- Add restrained blue/teal shade variations, subtle card borders/shadows and
  consistent corners instead of oversized pill-like panels.
- Improve meter-row hover/focus styling and gently separate the monthly
  recommendation from the other estimates; preserve existing content order.
- Retain stacked logo/navigation, all controls, readable contrast and clear
  actual-versus-estimated data. Update frontend README, context and changes.md.
- Aim for at most 100 changed implementation lines; tests/docs excluded.

## Reuse

- Existing MUI theme, components, local logos and browser-check helpers.
  No new dependencies, screens or design framework.

## Verify

- Frontend tests, TypeScript/Vite build and git diff --check.
- Desktop and 320px/390px login, meter list/details, forms and account menu:
  readable text, visible focus, adequate contrast and no overflow.

## Out of scope

- Feature, forecast, wording, backend, database or permission changes; artwork
  edits, major redesign, full Ticket 65 review, siblings, commits and pushes.
