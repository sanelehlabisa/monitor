# Task 043: Monitor logo and blue-teal theme

## Aim

Complete Ticket 58 by giving Monitor its supplied identity and a consistent
logo-led colour theme, without changing application behaviour.

## Clarifications

- Compact Monitor logo/name above login and the signed-in workspace: approved.
- Blue headers/buttons, white/light-blue surfaces and teal accents: approved.
- Small Roventics logo linking to roventics.com in the footer: approved.
- Keep layout, fonts and functionality otherwise unchanged: approved.

## Change

- Reuse public/monitor-logo.png unchanged for app branding and browser favicon;
  update the page title to Monitor and browser theme colour to the new blue.
- Use the existing local Roventics image for a modest footer acknowledgement
  linking to https://roventics.com in a safely configured new tab.
- Update the shared MUI palette and existing hardcoded section/tab/control
  colours: deep blue primary, readable teal accents, white/light-blue surfaces.
  Keep semantic warning/error colours distinct and text contrast readable.
- Preserve compact typography, the 42px account icon, Back/account navigation,
  forms/history, routes, permissions and forecast wording/math.
- Update relevant rendering checks, README/roadmap/context and changes.md.
  Aim for at most 100 changed implementation lines; tests/docs/assets excluded.

## Reuse

- User-supplied transparent Monitor PNG, existing Roventics PNG, MUI theme,
  components/navigation and existing browser verification helpers. No new dependency.

## Verify

- Frontend checks, TypeScript/Vite build and git diff --check.
- Desktop and 320px/390px phone login, meter list/detail, active tabs, account
  menu, record forms and forecast states; readable contrast and no overflow.
- Correct logo/favicon/title/theme metadata, both local image responses and
  the Roventics link; preserve both source-image hashes and existing data.

## Out of scope

- Full Ticket 65 usability work, new features, backend/SQL/schema, DB writes,
  authentication/forecast changes, fonts/layout redesign, generated/reworked
  logos, PWA/native apps, sibling edits, deployment and commits/pushes.
