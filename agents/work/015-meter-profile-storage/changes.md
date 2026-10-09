# Task 015: Meter profile storage

## Result

Nickname-only software meter profiles now persist in PostgreSQL through raw
Psycopg operations. Each meter belongs to one verified user and supports create,
list, retrieve, rename and delete operations.

## Change

- Added migration `004_meter_profiles.sql` with UUID IDs, owner foreign keys,
  trimmed 1-80 character names, timestamps and case-insensitive per-owner name
  uniqueness.
- Added the typed `Meter` repository and explicit errors for missing meters and
  duplicate names.
- Owner-scoped repository calls hide another user's meter; passing the explicit
  unrestricted scope supports the approved administrator API in Task 016.
- Added integration coverage for CRUD, ordering, cross-owner isolation,
  unrestricted listing, name normalization, conflicts and database constraints.
- Updated backend and database documentation. No ORM or new dependency was
  introduced.

## Reuse

- Reused the existing migration runner, direct database connection, transaction
  pattern, typed immutable records and PostgreSQL integration-test approach.

## Verification

- Focused repository tests: 2 passed.
- Full backend suite: 37 passed.
- Migration `004_meter_profiles.sql` applied successfully during the test run.
- `git diff --check` passed; only line-ending notices were reported.
- `refocus.md` was present and untracked at the start of the task, then became
  absent without being targeted by any task command or patch. No replacement
  was fabricated and it is excluded from the commit.
