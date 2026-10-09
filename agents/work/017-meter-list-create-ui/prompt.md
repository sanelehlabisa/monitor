# Task 017: Meter list and create UI

## Aim

Let an authenticated user add a nickname-only meter, see the accessible meter
list, and select a meter in the mobile-first Material UI application.

## Clarifications

- Question: What fields are required? Answer: Only a short meter/property name,
  such as Home or Shop.
- Question: What should selection show before ledger work exists? Answer: An
  honest selected-meter view with the name and a `Not enough data` state, without
  inventing balances or forecasts.
- Question: What visual direction applies? Answer: Continue the Task 014
  Switch-inspired compact cards and approved Roventics logo using native MUI.

## Change

- Add typed frontend API calls for meter listing, creation, and retrieval.
- Replace the static empty state with loading, error, empty, create, and populated
  meter states.
- Add a one-name create flow that is quick on mobile and handles duplicate or
  invalid names clearly.
- Allow selecting a meter and returning to the list without adding routing or a
  new dependency.
- Show an honest placeholder for the later balance/top-up dashboard.
- Add focused UI/API tests and update frontend/project documentation and
  changes.md.

## Reuse

- Reuse the Task 014 session shell, relative `/api` client, MUI theme/cards,
  Roventics logo, and existing responsive layout.

## Verify

- Run frontend tests and the production build.
- Validate login, create, list, select, refresh, and empty/error states against
  the running development stack at desktop and narrow mobile widths.
- Run `git diff --check`.

## Out of scope

- Rename/delete controls, cross-owner admin presentation, balance/top-up forms,
  charts, forecasts, tariffs, Rand amounts, OCR, hardware, and ML.
