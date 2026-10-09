# Task 021: Manual ledger API

## Aim

Expose authenticated CRUD APIs for actual balances and purchased-kWh top-ups on
an accessible meter.

## Clarifications

- Question: Who may manage entries? Answer: Regular users may manage entries on
  their meters; configured administrators may manage entries on every meter.
- Question: Are future events accepted? Answer: No. Occurrence times must be
  timezone-aware and no later than request time.
- Question: What can be corrected? Answer: Both kWh and occurrence time may be
  updated; delete is also supported.
- Question: How are inaccessible IDs handled? Answer: Missing, foreign meter and
  foreign entry IDs return the same generic 404.

## Change

- Add nested authenticated balance and top-up list/create/get/update/delete
  routes below `/api/meters/{meter_id}`.
- Validate Decimal kWh precision/range, timezone-aware timestamps and no-future
  occurrence times at the API boundary.
- Apply the established regular-user/admin meter scope to every request and
  ensure each entry belongs to the path meter.
- Return 409 for duplicate balance times, 422 for invalid values/times and 404
  for inaccessible resources.
- Add integration tests for CRUD, future-time validation, ownership, entry/meter
  mismatch and administrator access; update backend documentation.

## Reuse

- Reuse the cookie-session dependency, admin scope policy, meter lookup,
  Task 019/020 repositories and existing response/error conventions.

## Verify

- Run focused ledger API tests and the full backend suite in Compose.
- Exercise standard-user and administrator HTTP flows through the live stack.
- Run `git diff --check`.

## Out of scope

- Frontend UI, forecast calculations, combined dashboard summaries, reminders,
  tariffs, Rand amounts, payments, OCR, hardware and ML.
