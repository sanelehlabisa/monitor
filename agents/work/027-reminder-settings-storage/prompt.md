# Task 027: Reminder settings storage

## Aim

Persist optional per-meter email reminder preferences using explicit PostgreSQL
schema and raw SQL.

## Clarifications

- Question: Are reminders enabled automatically? Answer: No. Monthly and
  low-balance reminders are independently disabled until the user opts in.
- Question: What can users configure? Answer: Monthly day 1-28, low-balance
  warning lead time defaulting to 3 days, and an IANA timezone captured from the
  browser.
- Question: Who owns settings? Answer: One settings record belongs to one meter
  and is deleted with it; existing owner/admin meter scope applies.

## Change

- Add a forward-only migration for one optional reminder-settings row per meter.
- Store monthly enabled/day, low-balance enabled/lead days, timezone and audit
  timestamps with database constraints.
- Add typed raw-SQL get/upsert functions with timezone and value validation.
- Return clear defaults for a meter without saved preferences without silently
  enabling email.
- Add live-PostgreSQL repository tests for defaults, updates, validation,
  ownership/admin scope and cascade deletion.

## Reuse

- Reuse meter ownership checks, Psycopg transaction patterns and the existing
  Decimal/timezone conventions; add no ORM or environment setting.

## Verify

- Run focused repository tests, migration checks and the complete backend suite.
- Run `git diff --check`.

## Out of scope

- Delivery logs, email sending, runner/scheduler, HTTP, UI, SMS, push and payment
  reminders.
