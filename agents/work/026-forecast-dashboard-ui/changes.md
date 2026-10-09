# Task 026: Forecast dashboard UI

## Result

Ticket 54 is complete. Selecting a meter now shows factual latest-balance data
and honest planning estimates from the backend's replaceable forecast model.

## Interface and reuse

- Added a typed dashboard client and a compact mobile-first Material UI forecast
  panel for estimated balance, daily use, remaining days, run-out date and the
  recommended 30-day kWh top-up.
- Keeps latest actual balance/time visually separate and shows calculation time,
  interval count and the no-buffer assumption.
- Shows `Not enough data` and `Inconsistent history` without placeholder
  estimates; valid zero use explains that no finite run-out exists.
- Reuses the existing selected-meter workspace and ledger controls. Successful
  creates, corrections and deletions reload the dashboard, so the browser never
  duplicates forecast mathematics.
- A failed post-mutation refresh reports that the ledger change succeeded and
  asks the user to reopen the meter instead of encouraging a duplicate save.

## Verification

- Frontend tests: 16 passed, covering the dashboard API client plus insufficient,
  inconsistent, zero-use and available forecast rendering.
- TypeScript validation and Vite production build passed; 904 modules were
  transformed.
- Complete backend suite: 53 passed.
- Live frontend-proxy flow changed from `not_enough_data` to `available` after a
  second balance, refreshed the usage rate after an admin correction, and
  returned to `not_enough_data` after the admin removed one reading.
- The synthetic Task 026 user was removed and both live sessions logged out.
- `docker compose config --quiet` and `git diff --check` passed.
