# Task 044: Compact brand navigation

## Aim

Save header space by aligning navigation beside one stacked logo/name block.

## Clarifications

- Logo above Monitor forms one combined block; Back and the account control
  align vertically with that whole block, not either element separately.
- Retain the existing account dropdown and Sign out action; no new Exit button.
- Proposed phone treatment: show the account icon only, with the full email
  retained inside its menu; desktop keeps the email beside the icon.

## Change

- Use one compact row: Back left, stacked logo/name centred, account right.
- Keep centred branding on login/loading and omit unavailable navigation actions.
- Preserve the 48px logo, 42px account icon, palette, fonts and busy-state guards.
- Update focused checks, frontend README, context and changes.md.
- Aim for at most 100 changed implementation lines; tests/docs excluded.

## Reuse

- Existing App header, Navigation component, MUI layout and browser checks;
  reuse both logo assets unchanged. No new dependency.

## Verify

- Frontend tests, TypeScript/Vite build and git diff --check.
- Desktop and 320px/390px login, meter list/detail and account menu: centred
  combined branding, vertically aligned actions, working Back/Sign out, no overflow.

## Out of scope

- Other layout/features, backend, database writes, forecast/auth changes, artwork
  edits, full Ticket 65, sibling repositories, commits and pushes.
