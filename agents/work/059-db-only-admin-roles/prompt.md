# Task 059: DB-only administrator roles

## Aim

Implement Ticket 69.3: make users.type the sole administrator authority and safely
transition the current development database without losing existing data.

## Clarifications

- The user chose a safe current-DB upgrade after a fresh backup and successful
  isolated rehearsal; no reset, replacement or fresh-seed replay.
- Promote only the existing hlabisasanele730@gmail.com account once; all other
  existing users remain user. If that account is absent, stop and ask rather
  than create it. Later role changes are manual DB edits, never email overrides.
- Keep signup open, ordinary users owner-scoped and admins unrestricted across
  all meters. Shared membership access remains a separate ticket.

## Change

- Read the stored type through existing OTP and session-user queries. Derive
  is_admin from that value on every authenticated request; keep public API and
  cookie shapes unchanged. New signups default to user; repeat login preserves
  stored roles. No role cache, extra privilege query or runtime promotion.
- Remove administrator environment configuration from settings, Compose, both
  committed env examples and existing ignored local env files. Remove only the
  admin setting locally; preserve unrelated values and never expose secrets.
- Resolve the exact source container/volume/schema and require application/
  reminder writers to remain stopped. Make a new consistent full-DB backup in
  a fresh restricted %LOCALAPPDATA%/Monitor/backups/task059/ directory outside
  Git/OneDrive; retain its hash, private evidence and recovery instructions.
- Restore and verify that backup in isolated labelled resources, then rehearse
  upgrade-058.sql and the exact one-time admin assignment. Verify the new code
  before source changes. Recheck source identity/state against the backup, then
  apply the reviewed additive upgrade and assignment to the current DB only.
  Preserve both migration histories, owner fields and all original records.
- Respect upgrade-058.sql's own transaction, followed by a guarded one-time role
  transaction; do not nest it in an outer transaction. Stop on any failure before
  cutover. Existing stopped containers may retain old env metadata; do not restart
  them to clear it, and never use that metadata as a privilege fallback.
- Retain fresh-only seeding; never run schema.sql/seed.sql against existing data.
  Keep the original frontend/backend/Mailpit stopped. If preconditions or service
  state differ, stop before live writes; do not improvise a reset or rollback.
- Update relevant READMEs, context, roadmap and changes.md with actual results,
  recovery boundaries and remaining sharing work. Keep implementation small.

## Reuse

- Existing User, OTP/session queries, authenticated-user dependency and meter
  scope helpers; Task 058 schema/upgrade, raw Psycopg and existing tests; Tasks
  057-058 snapshot, private-comparison and isolated recovery methods.

## Verify

- Isolated checks: fresh/returning OTP users retain correct types; promotion and
  demotion affect /api/me and foreign-meter access on the next request with the
  same cookie. Verify admin CRUD, regular-user isolation and no env/email bypass.
- Verify default user, fresh admin seed and preserved manual demotion; reuse
  OTP/session/ledger/dashboard/reminder checks without changing their contracts.
  All write tests/mail use explicit isolated DB/Mailpit, never live accounts.
- Before/after live upgrade, privately compare original-column records, IDs,
  auth/ledger state, sequence, constraints and both histories; check added owner
  memberships/types separately and exactly the one approved admin assignment.
- Keep backups/evidence private and not encrypted by default. Remove only exact
  identity-checked task resources; retain recovery backup. Check active admin-env
  removal, links, whitespace, file scope and unchanged source service state.

## Out of scope

- Account creation or OTP/session writes on the source; automatic migrations,
  seed replay, runtime email privilege or env fallback; sharing/deletion-policy
  changes; forecast/UI/reminder changes; dependencies; real email; deployment;
  restarting/starting source services; siblings; commits/pushes.
