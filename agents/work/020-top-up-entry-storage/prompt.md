# Task 020: Top-up entry storage

## Aim

Persist manually purchased top-up energy in kWh through explicit SQL and a small
owner-aware repository.

## Clarifications

- Question: What does top-up mean? Answer: Energy already purchased and added,
  entered in kWh only; Monitor does not sell electricity or accept Rand values.
- Question: What values are valid? Answer: Top-up kWh must be greater than zero
  and supports at most three decimal places.
- Question: Can times repeat? Answer: Yes. Multiple purchases may share the same
  occurrence time and are ordered deterministically by ID.
- Question: How are corrections handled? Answer: Authorized users may edit kWh
  and occurrence time or delete an entry, retaining created/updated timestamps.

## Change

- Add a forward-only migration for `top_up_entries` with UUID IDs, cascading
  meter ownership, positive `NUMERIC(12,3)` kWh and occurrence/audit times.
- Add typed raw-Psycopg create/list/get/update/delete functions with explicit
  meter and optional owner scopes.
- Map missing entries to a domain error and list newest-first with a stable ID
  tiebreaker.
- Add repository integration tests and update database/backend documentation.

## Reuse

- Reuse Task 019's validated decimal, scoped CRUD, ordering, transaction and
  PostgreSQL test patterns without introducing a generic ORM-like abstraction.

## Verify

- Run focused top-up repository tests and the full backend suite in Compose.
- Confirm constraints, repeated times, cross-owner isolation, edits and deletes.
- Run `git diff --check`.

## Out of scope

- HTTP routes, UI, forecasts, reminders, payments, tariffs, Rand amounts, OCR,
  hardware, MQTT and ML.
