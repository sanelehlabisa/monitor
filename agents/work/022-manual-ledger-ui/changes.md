# Task 022: Manual ledger UI

## Result

Tickets 50 and 51 are complete. Users can record, review, correct and delete
actual balance and purchased-top-up kWh entries from a selected meter without
introducing forecasts early.

## Interface

- Added typed cookie-authenticated frontend calls for both nested ledger APIs.
- Added compact Material UI balance/top-up modes with decimal kWh and editable
  local date/time fields defaulted to now.
- Shows the latest actual balance separately and combines both factual record
  types into a clearly labelled newest-first history.
- Added correction and browser-confirmed deletion for both record types with
  visible duplicate, validation, missing-resource and request errors.
- Clears history during meter changes so a failed request cannot display another
  meter's stale entries.
- Retained `Not enough data`; no estimated value is derived in this task.

## Reuse

- Reused the selected-meter workspace, session-aware request helper, Task 021
  endpoints, administrator access behavior and existing Material UI patterns.
- Added no dependency, router, ORM or forecasting implementation.

## Verification

- Frontend tests: 12 passed, covering both API contracts plus populated and
  empty factual ledger states.
- TypeScript validation and Vite production build passed; 903 modules were
  transformed.
- Full backend suite: 44 passed.
- Live flow through the frontend proxy created and listed both record types as a
  regular user, returned 404 for a different user's ledger access, and allowed
  the configured admin to find the meter, correct its balance and delete its
  top-up and meter with 204 responses.
- Direct post-flow checks found zero Task 022 meters, balances or top-ups; all
  synthetic Task 022 challenges and users were removed and sessions logged out.
- `docker compose config --quiet` and `git diff --check` passed. Diff checking
  reported only the repository's existing LF-to-CRLF notices.
