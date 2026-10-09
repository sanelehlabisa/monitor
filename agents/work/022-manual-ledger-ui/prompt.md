# Task 022: Manual ledger UI

## Aim

Let users quickly record, review, correct and delete actual balance and purchased
top-up kWh entries for the selected meter.

## Clarifications

- Question: What are the primary actions? Answer: `Record balance` and `Record
  top-up`, each requiring kWh plus an editable local date/time defaulted to now.
- Question: How is history shown? Answer: One compact newest-first history that
  clearly labels actual balances versus purchased top-ups and their times.
- Question: What access applies? Answer: Users manage their own selected meter;
  admins use the same controls on every accessible meter.
- Question: Are forecasts included? Answer: No. The selected meter continues to
  show `Not enough data` until the later Ticket 52 forecasting batch.

## Change

- Add typed frontend CRUD calls for balance and top-up endpoints.
- Add compact MUI forms with decimal kWh inputs and local `datetime-local`
  values defaulted to now.
- Load and combine both histories newest-first with clear Actual balance and
  Purchased top-up labels.
- Add edit and confirmed-delete flows for both entry kinds, with visible
  validation, duplicate-time, missing and network errors.
- Keep latest actual balance visibly factual and do not derive forecasts.
- Cover empty/loading/error/history/edit/delete/admin states with tests and a
  live end-to-end flow; update roadmap/context/component documentation.

## Reuse

- Reuse the selected-meter workspace, session-aware API helper, admin
  presentation, MUI cards/feedback and established mutation state patterns.

## Verify

- Run frontend tests and production build plus the full backend suite.
- Validate create/list/edit/delete for both entry types through the frontend
  proxy at narrow and desktop layouts.
- Verify regular-user isolation and administrator management.
- Run `docker compose config --quiet` and `git diff --check`.

## Out of scope

- Forecasting, estimated balance/days/run-out, 30-day recommendations,
  reminders, charts, tariffs, Rand amounts, payments, OCR, hardware and ML.
