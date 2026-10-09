# Task 025: Dashboard API

## Result

Authenticated clients can request one current meter dashboard containing
factual ledger data and a freshly derived forecast.

## Change and reuse

- Added `GET /api/meters/{meter_id}/dashboard` with typed actual, history and
  estimate response sections.
- Reused existing raw-SQL repositories and owner/admin scope; no forecast table
  or cache was added.
- Calls only the single `run_forecast_model` function, keeping the calculation
  replaceable without HTTP changes.
- Returns separate balance/top-up lists plus a labelled combined newest-first
  history and latest factual actual balance.

## Verification

- Focused live-PostgreSQL dashboard integration test: 1 passed.
- Complete backend suite: 53 passed.
- Covered unauthenticated, insufficient, available, inconsistent, corrected,
  foreign-user and administrator states.
- Live frontend-proxy flow returned an available forecast and three factual
  history items to its owner and configured admin; admin deletion returned 204.
- The synthetic Task 025 user was removed and both live sessions logged out.
- `docker compose config --quiet` and `git diff --check` passed.
