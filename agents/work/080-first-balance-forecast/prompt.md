# Task 080: Forecast from the first balance

## Aim

Show useful, clearly labelled initial estimates immediately after the first balance,
then calculate usage from that meter's own history as readings accumulate.

## Clarifications

- The user directly requested the first-balance fallback and immediate updates.
  This supersedes the former two-reading gate for all forecasts.
- Use the previously discussed 10 kWh/day starting assumption in one backend
  constant. The synthetic research regression/prior was never integrated and is
  not validated household data.
- The user confirmed: update existing dashboard estimates only; no charts.

## Change

- With one actual balance at or before calculation time, use the default rate
  and existing elapsed-time/top-up/current-balance/run-out/calendar calculations.
- With two or more valid readings, retain the existing per-meter observed rate.
  No balance remains unavailable; inconsistent history must not use a fallback.
- Reuse available status and intervals_used=0 to label the default in the UI
  and monthly email text. Keep legacy low-balance warnings measured-only.
- Verify existing add/edit/delete dashboard refresh paths, update stale copy
  and current documentation, and preserve existing monthly amount semantics.

## Reuse

run_forecast_model, Decimal/time helpers, dashboard reload guards and forecast UI.

## Verify

Focused forecast/calendar/API checks for first balance, elapsed time, top-ups,
zero/depleted balance, future/invalid data, measured-rate transition, edits and
deletions. Check fallback labeling, build frontend and run existing UI checks.
Use synthetic isolated data only; preserve running app, actual env and database.

## Out of scope

Research regression integration, new libraries, schema or API shape changes,
new charts, reminder activation, service recreation,
live data edits, commits and pushes.
