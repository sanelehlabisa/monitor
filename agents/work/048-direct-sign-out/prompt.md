# Task 048: Direct sign out

## Aim

Simplify navigation with a visible red Sign out button and black company credit.

## Clarifications

- Replace the user icon/dropdown with a red Sign out button at the top right
  on phones, tablets and desktop.
- Keep the email beside it with a small gap; truncate long emails as needed.
- Make the footer's by Roventics text black, retaining its logo and link.

## Change

- Remove the avatar, account menu and unused menu state/imports.
- Reuse the existing logout handler directly; retain pending-state protection,
  Back on the left and the stacked Monitor logo/name.
- Keep email and Sign out aligned without overlap on narrow screens.
- Change only the company-credit text colour, not artwork or link behaviour.
- Update focused checks, frontend README, context and changes.md. Preserve
  uncommitted Tasks 045–047; aim for at most 100 implementation lines changed.

## Reuse

- Existing MUI navigation/buttons, logout handler, theme and local logo assets.

## Verify

- Frontend tests, TypeScript/Vite build and git diff --check.
- Phone/tablet/desktop: email/button alignment, long-email truncation, readable
  red button, keyboard focus, pending state, working Back and direct sign out.
- Black footer credit with unchanged company logo/link.

## Out of scope

- Backend, data, forecasting, routes/permissions, other layout changes,
  dependencies, siblings, commits and pushes.
