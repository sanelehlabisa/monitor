# Task 019: Balance entry storage

## Result

Actual remaining-balance observations now persist in PostgreSQL through a typed
raw-Psycopg repository with meter ownership enforcement.

## Change

- Added migration `005_balance_entries.sql` with UUID IDs, cascading meter
  ownership, non-negative `NUMERIC(12,3)` kWh, occurrence/audit timestamps and
  unique occurrence time per meter.
- Added shared validation that rejects naive timestamps, non-finite values,
  meaningful precision beyond three decimals and values outside storage range
  without silently rounding.
- Added owner-scoped/admin-ready create, newest-first list, get, correction and
  delete repository operations.
- Added explicit missing-entry and duplicate-time domain errors.
- Added integration coverage for ordering, conflicts, cross-owner isolation,
  unrestricted admin scope, correction, deletion and database constraints.

## Reuse

- Reused meter ownership lookups, UUID records, Psycopg transactions, cascading
  cleanup and the established PostgreSQL integration-test approach.

## Verification

- Focused balance repository tests: 2 passed.
- Full backend suite: 41 passed.
- Migration 005 applied successfully.
- `git diff --check` passed with only line-ending notices.
