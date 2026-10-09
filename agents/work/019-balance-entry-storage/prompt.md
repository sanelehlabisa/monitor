# Task 019: Balance entry storage

## Aim

Persist actual remaining-balance observations in kWh through explicit SQL and a
small owner-aware repository.

## Clarifications

- Question: What values are valid? Answer: Balance is kWh, may be zero or
  positive, and supports at most three decimal places.
- Question: How are times handled? Answer: The observation date/time defaults to
  now in the UI, remains editable, requires timezone-aware API input and is stored
  as PostgreSQL `TIMESTAMPTZ` in UTC.
- Question: Are duplicate observations allowed? Answer: A meter may have only
  one actual balance at an exact occurrence time.
- Question: How are corrections handled? Answer: Authorized users may edit kWh
  and occurrence time or delete an entry. V1 retains created/updated timestamps,
  not a complete revision history.

## Change

- Add a forward-only migration for `balance_entries` with UUID IDs, cascading
  meter ownership, non-negative `NUMERIC(12,3)` kWh, occurrence/audit times and
  per-meter occurrence uniqueness.
- Add typed raw-Psycopg create/list/get/update/delete functions with explicit
  meter and optional owner scopes.
- Map missing entries and duplicate occurrence times to domain errors.
- List entries newest-first with a deterministic ID tiebreaker.
- Add repository integration tests and update database/backend documentation.

## Reuse

- Reuse Task 015's UUID, ownership-scope, immutable record, transaction and
  raw-SQL integration-test patterns.

## Verify

- Run focused balance repository tests and the full backend suite in Compose.
- Confirm migration constraints, cross-owner isolation, corrections and deletes.
- Run `git diff --check`.

## Out of scope

- HTTP routes, UI, top-ups, forecasts, reminders, tariffs, Rand amounts, OCR,
  hardware, MQTT and ML.
