# Task 015: Meter profile storage

## Aim

Persist nickname-only software meter profiles with explicit SQL and a small,
tested repository boundary.

## Clarifications

- Question: What is a device in V1? Answer: A software meter/property profile
  with only a user-provided name; it is not hardware and has no meter number.
- Question: Who controls meters? Answer: A regular user controls their own
  meters, while configured administrators will control every user's meters at
  the API boundary in Task 016.
- Question: Is deletion allowed? Answer: Yes. Users can fully manage their own
  meters and administrators can fully manage all meters.

## Change

- Add a forward-only migration for user-owned meter profiles with an opaque ID,
  trimmed non-empty name, ownership, case-insensitive per-owner name uniqueness,
  and created/updated timestamps.
- Add typed raw-Psycopg repository operations to create, list, retrieve, rename,
  and delete meters, including owner-scoped and administrator-ready lookups.
- Map duplicate names and missing meters to explicit domain errors.
- Add repository integration tests for constraints, CRUD, ordering, and owner
  isolation.
- Update the database/backend context and record actual results in changes.md.

## Reuse

- Reuse the migration runner, database connection boundary, typed repository
  style, and PostgreSQL test fixtures already used by authentication.

## Verify

- Run the focused meter repository tests through the development Compose stack.
- Run the backend test suite and migration startup check.
- Run `git diff --check`.

## Out of scope

- HTTP routes, frontend controls, balance/top-up entries, forecasts, tariffs,
  payments, physical devices, OCR, MQTT, and ML.
