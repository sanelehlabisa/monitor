# Task 039: Minimal navigation and consistent typography

## Aim

Simplify navigation and make text sizing/alignment consistent (Ticket 62).

## Clarifications

- Remove the navigation logo, Roventics Monitor name and Admin badge.
- Keep Back on the left, email/account menu on the right; enlarge the user icon.
- The user confirmed 16px body text and 20–22px headings/forecast values, using
  the same font throughout. Vertically centre meter name and owner on desktop;
  keep a left-aligned stack on phones.

## Change

- Remove those navigation elements without deleting the logo asset. Rename
  Back to meters to Back; preserve the dropdown and distinct black Logout action.
- Enlarge the account icon and adjust the responsive single-row navigation.
- Reuse the MUI theme for a consistent font/small type scale, avoiding tiny
  labels and oversized headings. Align the meter name and owner vertically.
- Update relevant README/context and record results in changes.md. Stay within
  100 changed implementation lines and preserve Tasks 037–038.

## Reuse

- Existing Navigation, MeterWorkspace, MUI theme, forecast UI and browser checks.

## Verify

- Check desktop/320px/390px navigation, icon sizing, dropdown/Back, readable text
  and name/owner alignment without overflow. Retain demo data unchanged.
- Run relevant frontend checks, asset build and diff check; record actual results.

## Out of scope

- Backend, forecasts, permissions, routes, database/demo history, dependencies,
  new branding or deployment. No commit/push without a new request.
