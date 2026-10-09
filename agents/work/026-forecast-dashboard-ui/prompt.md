# Task 026: Forecast dashboard UI

## Aim

Show honest, mobile-first electricity planning estimates for the selected meter.

## Clarifications

- Question: Which data source is authoritative? Answer: The Task 025 dashboard
  endpoint; the browser does not reimplement forecast mathematics.
- Question: What should users see? Answer: Latest actual reading and time,
  estimated current balance, daily use, remaining days, run-out/next-top-up date
  and recommended 30-day top-up kWh.
- Question: How are unavailable forecasts shown? Answer: Keep clear `Not enough
  data` or `Inconsistent history` states and never render placeholder numbers.
- Question: When do estimates refresh? Answer: On meter selection and after
  every successful balance/top-up create, correction or deletion.

## Change

- Add typed dashboard API client models and refresh handling.
- Replace the static forecast placeholder with compact Material UI estimate
  cards while keeping latest actual data visually distinct.
- Show the model calculation time and concise assumptions.
- Retain existing manual entry/history controls and user/admin behavior.
- Add component/API tests for unavailable, inconsistent, zero-use and available
  forecast states plus refresh wiring after ledger changes.

## Reuse

- Reuse the selected-meter workspace, LedgerPanel, API helper, Roventics theme
  and existing loading/error patterns.

## Verify

- Run frontend tests and the production build plus the complete backend suite.
- Validate user/admin forecast refresh through the frontend proxy.
- Run `docker compose config --quiet` and `git diff --check`.

## Out of scope

- Browser-side forecast math, charts, reminders, configurable buffers, tariffs,
  Rand amounts, payments, hardware, OCR and ML.
