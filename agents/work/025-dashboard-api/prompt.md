# Task 025: Dashboard API

## Aim

Expose one authorised meter dashboard response containing factual history and
the replaceable forecast-model result.

## Clarifications

- Question: Which forecast implementation does HTTP call? Answer: Only Task
  023's public `run_forecast_model` boundary.
- Question: What does the response include? Answer: Latest actual balance,
  separate balance/top-up records, a combined newest-first factual history and
  forecast status/output with an explicit calculation time.
- Question: What access rules apply? Answer: Existing owner/admin meter scope;
  missing and inaccessible meters retain the same generic 404.
- Question: Is forecast output stored? Answer: No, it is recalculated from the
  current raw-SQL ledger on every request.

## Change

- Add `GET /api/meters/{meter_id}/dashboard` with typed response models.
- Load ledger records through existing owner-scoped repositories and pass them
  into the single forecast function.
- Serialize Decimal values exactly and label actual versus estimated fields.
- Add API integration coverage for insufficient, available, inconsistent,
  corrected-history, regular-user isolation and administrator access states.

## Reuse

- Reuse cookie authentication, meter scope, raw-SQL ledger repositories and
  existing generic resource errors.

## Verify

- Run focused live-PostgreSQL integration tests and the complete backend suite.
- Exercise the endpoint through the frontend proxy for user/admin access.
- Run `docker compose config --quiet` and `git diff --check`.

## Out of scope

- New tables, cached forecasts, mutation endpoints, UI, reminders, charts,
  tariffs, Rand amounts, hardware, OCR and ML.
