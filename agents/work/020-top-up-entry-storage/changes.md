# Task 020: Top-up entry storage

## Result

Manually purchased top-up energy now persists in PostgreSQL through a typed
raw-Psycopg repository with meter ownership enforcement.

## Change

- Added migration `006_top_up_entries.sql` with UUID IDs, cascading meter
  ownership, positive `NUMERIC(12,3)` kWh and occurrence/audit timestamps.
- Allowed multiple purchases at the same occurrence time and ordered equal-time
  rows deterministically by UUID.
- Added owner-scoped/admin-ready create, newest-first list, get, correction and
  delete repository operations.
- Reused shared strict decimal and timezone-aware timestamp validation.
- Added integration coverage for repeated times, ordering, cross-owner
  isolation, unrestricted admin scope, corrections, deletion and constraints.

## Reuse

- Reused Task 019's kWh/time validators and the established meter access,
  transaction, immutable-record and PostgreSQL test patterns.

## Verification

- Focused top-up repository tests: 2 passed.
- Full backend suite: 43 passed.
- Migration 006 applied successfully.
- `git diff --check` passed with only line-ending notices.
