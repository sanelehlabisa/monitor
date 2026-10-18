# Task 058: Fresh SQL bootstrap

## Aim

Implement Ticket 69.2's simpler fresh-install setup and rehearse a data-preserving
existing-database upgrade on an isolated copy only.

## Clarifications

- Preserve all existing data; test the upgrade on a copy only. Applying it to
  the current database requires separate approval.
- Keep current ownership, authentication, forecasts and environment-based admin
  behaviour working. DB-only role authority belongs to Task 059.

## Change

- Consolidate the existing eight domain tables into schema.sql, retaining their
  keys, constraints, indexes, digests, kWh precision and occurrence/audit times.
  Add users.type, NOT NULL/default user, constrained to user/admin; add user_meters
  with composite (user_id, meter_id) primary key, cascading user/meter FKs and a
  meter-first index. Retain meters.user_id and owner-name indexes as a bridge;
  shared access/deletion guards are not activated here.
- Add fresh-only seed.sql with the approved hlabisasanele730@gmail.com admin
  account and small fictional meter/ledger examples with owner memberships.
  No credentials, enabled reminders, startup re-promotion or seed replay.
- Mount schema then seed for PostgreSQL empty-volume initialization. Remove
  backend migration execution/mounts from Compose and migration calls from
  integration checks; retain historical migration sources inactive. Do not
  fabricate migration records on fresh installs. Preserve the named data volume,
  explicit environment values and backend/frontend reload.
- Mark the legacy migration CLI unsupported for schema.sql databases. Fresh
  initialization is once per empty volume, not SQL replay/idempotency; diagnose
  partial initialization failures without automatic resets.
- Provide an explicit additive upgrade SQL/procedure: add the same type and
  membership structure and backfill current owners. Rehearse only against the
  verified backup on a labelled isolated target; never run fresh seeds or
  promote existing accounts there. Preserve both migration-history tables.
  Repeat owner backfill at the later sharing cutover for interim new meters.
- Update relevant READMEs/context/roadmap and changes.md with actual results,
  recovery boundaries and the separately approved live-upgrade requirement.
- Review-size exception: approximately 200-300 implementation lines, mainly
  consolidating the existing 143 SQL lines plus seeds/upgrade/bootstrap wiring;
  tests/docs excluded. This remains one coherent initialization change.

## Reuse

- Existing SQL, Psycopg repositories, Compose/Docker targets, integration checks
  and Task 057's retained verified backup, manifest and recovery procedure.

## Verify

- Use only isolated task-labelled databases/app/Mailpit resources for writes.
  Set an explicit isolated test database URL; never run checks against the
  source or invoke base Compose commands that start its stopped services.
  Check fresh setup, constraints/FKs, UTC/kWh data, default user/admin seed and
  current OTP/session/meter/ledger/dashboard behaviour through existing checks.
  Assert seeded types directly in SQL, not as proof of active DB-based access.
- Check persistence after isolated restart/recreation: no duplicate seeds,
  overwritten manual demotion or ledger changes. Verify both reload paths.
- On the upgraded backup, compare all original-column records, auth/ledger state,
  IDs, sequence and both migration histories; check new types/memberships
  separately. No data loss or hidden reset; recovery is not upgrade evidence.
- Verify the current source remains logically unchanged. Retain private evidence
  outside Git/OneDrive; remove only identity-checked disposable resources.
  Check links, whitespace and scope; record limitations honestly.

## Out of scope

- Current-database writes/upgrades/seeds/resets or source service restarts;
  starting the stopped development stack; DB-admin runtime cutover/admin-env
  removal; shared authorization/UI or last-member guards; reminders/model/UI
  changes; new dependencies; real email; deployment; siblings; commits/pushes.
