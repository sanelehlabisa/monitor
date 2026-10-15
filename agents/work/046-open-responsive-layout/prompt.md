# Task 046: Open responsive layout

## Aim

Replace the card-heavy presentation with a simple, open phone/tablet workspace.

## Clarifications

- Card-free login and signed-in workspace direction: approved.
- Keep blue/teal branding, familiar actions and a simple mobile/tablet experience.

## Change

- Remove enclosing login/workspace cards and the large coloured forecast box.
- Use light page sections, slim headings, dividers and flat meter/detail rows.
- Present balance, days remaining and monthly recommendation directly on the
  page: stacked on phones, responsive columns on tablets/desktop.
- Keep record buttons prominent and forms/history on demand. Preserve logo/nav,
  admin tabs, controls, factual timestamps and honest unavailable states.
- Retain useful Task 045 typography/focus improvements and its uncommitted work.
  Update frontend README, context and changes.md.
- Aim for at most 100 changed implementation lines; tests/docs excluded.

## Reuse

- Existing React/MUI components, theme, handlers, assets and browser checks.
  No new dependency or screen.

## Verify

- Frontend tests, TypeScript/Vite build and git diff --check.
- Phone 320/390px, tablet 600/768/1024px and desktop: readable estimates,
  forms/navigation/admin tabs, keyboard focus, contrast and no overflow.

## Out of scope

- New features, wording/calculation changes, backend, database writes, routes,
  permissions, artwork, full Ticket 65 review, siblings, commits and pushes.
