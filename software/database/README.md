# Database

PostgreSQL with explicit Psycopg SQL; no ORM or automatic runtime migrations.

## Active files

- schema.sql: nine domain tables and constraints/indexes.
- seed.sql: fresh-development admin and fictional example meters/history.
- README.md: setup, safety and recovery guidance.

Compose mounts schema.sql then seed.sql read-only into PostgreSQL initialization.
They run only on an empty persistent volume; restart/recreation does not replay
SQL or overwrite roles/examples. The API never installs/upgrades SQL. Never
delete a volume or replay seeds as an upgrade/partial-init repair; preserve
evidence and approve an explicit repair first.

Task 059 safely upgraded the existing development DB. Do not rerun its one-time
upgrade or seeds. It has nine domain tables plus retained monitor.schema_migrations
and public.schema_migrations tables. Task 060 removes inactive sources, not either
stored history table or data.

## Tables and contracts

| Table | Purpose |
| --- | --- |
| users | Unique normalized email, audit time, constrained user/admin type. |
| otp_challenges | Email-keyed HMAC digests, expiry, attempts and used state. |
| user_sessions | User FK, unique token digest, expiry and revocation. |
| meters | UUID, owner user FK, trimmed name and audit times. |
| user_meters | Composite user/meter membership key and reverse lookup index. |
| balance_entries | Meter FK, non-negative NUMERIC(12,3) kWh, occurrence/audit times. |
| top_up_entries | Meter FK, positive NUMERIC(12,3) kWh, occurrence/audit times. |
| reminder_settings | Disabled-by-default monthly/low-balance preferences. |
| reminder_deliveries | Durable pending/sent claims and per-meter deduplication. |

OTP signup creates a user only after verification; plaintext OTPs/tokens are never
stored. Only users.type grants admin access, without env/email fallback. Fresh
seeds provision hlabisasanele730@gmail.com as admin and monitor-seed@example.test
examples, without credentials/sessions or enabled mail. Login/restart never
overwrites manual role changes; see the [backend README](../backend/README.md).

Meter names are case-insensitively unique per owner. Balances have unique
per-meter occurrence times; purchases may share a time. Store UTC instants,
preserving occurrence times separately from audit times. Rates/forecasts are
derived, not stored truth. Access remains owner/admin-based; membership rows
alone do not grant shared access or protect the last member.

## Verified recovery

Latest recovery set, outside Git/OneDrive:

    %LOCALAPPDATA%/Monitor/backups/task059/20261018T171408Z-4fbf46c4c3c5/

It contains pre-upgrade monitor.dump, RECOVERY.md, private manifest/inventories,
reviewed-upgrade-058.sql and reviewed-admin-assignment.sql. Access is restricted
to the Windows user/SYSTEM but is not encrypted. Never publish private evidence.

- monitor.dump: 25,316 bytes; SHA-256
  a14acd1536b5e7aa04c66a774c3baa5738ad5060e47a02310f8ad940f5524cd1.
- Exact retained upgrade copy:
  %LOCALAPPDATA%/Monitor/backups/task059/20261018T171408Z-4fbf46c4c3c5/reviewed-upgrade-058.sql
  SHA-256 c5ad664ee3e3febe924a9d096c802bbbbb1dd4363aff40c1f95d83943e9a3fe2.
- Retired migration SQL/runner and upgrade are recoverable from Git commit
  09db59a7d8ced4879f48d8534cb3b1e5dc101864. Task 060's exact-byte source archive
  and recovery checks are in its [work record](../../agents/work/060-retire-legacy-setup/changes.md).
- Earlier task057/task058 recovery/evidence sets remain untouched. Exact source
  identities, approvals and comparisons remain in their historical work records
  under agents/work/, including Task 059's
  [results](../../agents/work/059-db-only-admin-roles/changes.md).

Privately read RECOVERY.md and the manifest, verify dump/SQL hashes, and restore
only to a new isolated labelled container/volume using the pinned PostgreSQL
image and original role. Never mount/overwrite the source volume. Compare data,
IDs, auth state, constraints, both histories and sequence; advance sequences only
on the disposable copy. Logical backups exclude cluster roles/passwords/tablespaces.

The backup predates the upgrade. To rehearse that old-state transition, use the
exact retained reviewed SQL above, not schema.sql/seed.sql or an absent active
path. It is a one-time transaction with its own BEGIN/COMMIT/timeouts; use psql
ON_ERROR_STOP, never a second wrapping transaction. Verify original-column data
and default roles before separately rehearsing the reviewed admin assignment.
This guidance does not authorize live restoration/upgrade.

Task 059 preserved all data: 2 users, 4 meters/initial owner memberships,
7 balances, 4 top-ups, 16 challenges and 16 sessions; reminder tables were empty.
Only the approved existing account became admin. The DB stayed running; source
frontend/backend/Mailpit stayed stopped. Fresh/reload checks passed in 058;
68 isolated backend checks passed in 059. These are historical results, not a
new live-browser verification.

## Remaining database/access work

The [root roadmap](../../README.md) owns stable IDs and priority; the
[backend](../backend/README.md) and [frontend](../frontend/README.md) define detail.

- 69.1-69.3: recovery, fresh bootstrap and DB-only roles are complete.
- 69.4: shared authorization and concurrent last-member safety. Repeat owner
  membership backfill for interim meters; resolve creator-delete cascades,
  whole-meter deletion/onboarding/display before cutover.
- 69.5: minimal membership-aware UI/My/All/search after backend guards.
- 69.6: fixed 1st-of-month planning, separate from run-out/30-day quantities.
- 69.7: day-before monthly email to all meter members, not all accounts; retain
  low-balance eligibility and per-recipient dedupe/removal. Saved timezone/send
  time needs agreement; reuse the finite runner.
- 70: HTML email with plain fallback/trusted links after reminder rules.

Keep separate reminder preferences/claims, digest-only security and occurrence
times. Add no tables/triggers/procedures without need. Cleanup does not authorize
a live transition/reset, sharing activation, seed replay or future feature.
