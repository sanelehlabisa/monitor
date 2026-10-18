# Database

PostgreSQL uses explicit SQL through Psycopg; the project does not use an ORM.

## Current implementation

Task 058 changes fresh development setup to ordered, read-only PostgreSQL mounts:
`schema.sql` at `/docker-entrypoint-initdb.d/01-schema.sql`, then `seed.sql` at
`/docker-entrypoint-initdb.d/02-seed.sql`. Each file runs transactionally only
when the named PostgreSQL volume is empty; they are not replay/idempotency scripts.
The API no longer executes or mounts migrations. Backend/frontend reload and
the persistent volume are retained. Fresh/copy-upgrade and reload verification
passed; no current database upgrade or seed is authorized by this change.

Fresh `schema.sql` has nine domain tables: the existing eight below plus
`user_meters`, and constrained `users.type` defaulting to `user`. It creates no
fake migration history. The existing Task 057 source instead has eight domain
tables and **both** `monitor.schema_migrations` and `public.schema_migrations`;
preserve all of that data through any separately approved upgrade.

The eight SQL files in `migrations/` and `app.migrations` are retained historical
sources, not the supported initialization path. Do not edit applied history or
run the legacy CLI against a schema.sql database; its guard rejects the new
schema before creating migration bookkeeping. Fresh setup is not an existing-
volume upgrade. See 69.2 below for the explicit `upgrade-058.sql` procedure.

### Retained contracts and historical SQL

Migration `002_users_and_otp_challenges.sql` adds:

- `monitor.users`: unique normalized email and creation time; and
- `monitor.otp_challenges`: challenge UUID, normalized email, HMAC digest,
  creation/expiry, attempt count and used/invalidated timestamps.

Challenges intentionally reference email rather than a user ID because open
signup creates the user only after successful verification. Constraints reject
non-normalized emails, non-SHA256-shaped digests, invalid expiry and invalid
attempt counts. The email/creation index supports cooldown and hourly limits.

Plaintext OTPs are never persisted. Forecasts and sessions are not stored by this
migration.

Migration `003_user_sessions.sql` adds `monitor.user_sessions`. Each row belongs
to a verified user and stores a unique SHA-256 digest, creation/expiry times and
an optional revocation time. The plaintext 256-bit random token is delivered
through the existing HTTP-only cookie layer, not persisted. A user may have
multiple independent sessions, each with a fixed 30-day lifetime.

Migration `004_meter_profiles.sql` adds nickname-only `monitor.meters`. Each
meter has an application-generated UUID, one owning user, a trimmed 1-80
character name and creation/update timestamps. Names are case-insensitively
unique per owner. The raw-SQL repository provides owner-scoped CRUD plus an
explicit unrestricted scope for the administrator API.

Migration `005_balance_entries.sql` adds factual remaining-kWh observations.
Each UUID entry belongs to one meter, stores non-negative `NUMERIC(12,3)` kWh,
an occurrence time and creation/update timestamps. A meter cannot have two
actual balances at the same occurrence time. Deleting its meter cascades to its
balance history.

Migration `006_top_up_entries.sql` adds manually purchased energy events. Each
UUID entry belongs to one meter, stores positive `NUMERIC(12,3)` kWh plus
occurrence/audit timestamps, and is deleted with its meter. Multiple purchases
may share an occurrence time and are ordered deterministically by UUID.

Migration `007_reminder_settings.sql` adds one optional preference row per
meter. Monthly and predicted-low-balance emails are independently disabled by
default. Saved settings constrain monthly days to 1-28, positive warning lead
days to at most 30, and a trimmed IANA timezone name. Rows cascade with their
meter; email delivery history is introduced separately.

Migration `008_reminder_deliveries.sql` adds durable monthly/low-balance claims
with unique per-meter type/dedupe keys. Pending claims may be recovered by the
runner after a timeout; successful sends record their completion time. Rows
cascade with the meter and do not duplicate the owner's email address.

## Database/access refocus: Ticket 69

Task 056 planned these stages; Task 057 verified recovery and Task 058 implements
fresh bootstrap plus an isolated upgrade rehearsal. Each later implementation
needs its own approved prompt. Current owner scoping/environment-admin authority
remain unchanged; membership storage and DB types do not yet grant access.
The [root roadmap](../../README.md) owns execution order; backend details for
69.3 roles and 69.4 membership are in the [backend README](../backend/README.md).

### 69.1: Existing-data audit, backup/restore and target-schema review

Completed: Task 057 identified the source and verified isolated recovery; Task
058's approval accepts the additive target. Preserve all current data, never
overwrite the source to test restoration, and never commit private records.

The minimal target is nine domain tables, retaining existing names:

- `users`: normalized email, audit time and `type` (`user`/`admin`).
- `otp_challenges`: email-keyed signup challenges with digest, expiry, attempts,
  consumed/invalidated state and existing cooldown/rate-limit support.
- `user_sessions`: user FK, unique token digest, expiry and revocation state.
- `meters`: UUID, name and audit times; retain owner fields until 69.4/69.5.
- `user_meters`: user/meter FKs and a unique composite membership key.
- `balance_entries`: meter FK, non-negative kWh, occurrence/audit times and the
  existing unique per-meter occurrence constraint.
- `top_up_entries`: meter FK, positive kWh and occurrence/audit times; multiple
  purchases at the same time remain valid.
- `reminder_settings`: retain planning/low-balance configuration separately.
- `reminder_deliveries`: retain durable delivery claims/deduplication separately;
  69.7 defines per-recipient keys and member-removal handling.

Keep open email signup and secure cookie sessions: users are created only after
verification, and plaintext OTPs/session tokens never enter the database. Preserve
`occurred_at` separately from insertion/update times so historical manual entries
remain meaningful. Use timezone-aware UTC instants for storage and local display
at the client boundary. Consumption rates and forecasts remain derived from each
meter's ledger, not a second authoritative stored value or a new model.

Recovery and target acceptance do not authorize a source upgrade or reset.
Membership must prevent last-member removal, including concurrent removals
and account deletion; 69.4 defines transactional enforcement. Settle creator
display, sharing onboarding and whole-meter deletion with 69.4/69.5 prompts.
Saved reminder timezone/send time is resolved with 69.7, not inferred from UTC.
Do not introduce triggers, stored procedures or extra tables without a need.

#### Task 057: verified database recovery and cleanup

The user chose to preserve all existing data. Initial Docker-unavailable/stopped
attempts performed no database audit or backup. The user then explicitly approved
starting only the database. The completed audit verified PostgreSQL 17.11 in
`monitor-dev-database-1`, using `monitor-dev_postgres-data`; the other three
Monitor services remain stopped. No Docker Desktop restart was performed.

A held `REPEATABLE READ READ ONLY` transaction exported the snapshot used by
the complete custom-format `pg_dump --create` and private comparison inventory.
The backup was restored with original ownership/ACLs into the same pinned image,
with a separate labelled volume/container, no network or published ports, and no
application/email workers. Source and restore matched all table counts and
private canonical record fingerprints, schema/constraints/FKs/indexes,
ownership/ACLs/default ACLs, extensions/settings/policies/functions/triggers and
sequence state. Only the clone advanced its identity sequence, confirming the
next value was correct and above existing IDs.

Observed counts: 2 users, 4 meters, 7 balances, 4 top-ups, 16 OTP challenges and
16 sessions; reminder settings/deliveries are both empty. There are **10 physical
tables**: eight domain tables plus `monitor.schema_migrations` (8 rows) and
`public.schema_migrations` (1 row), with 38 constraints, 21 indexes and one
sequence. A monitor-only dump would omit the public bookkeeping table.

After verification the source retained the same logical state, container-start
time and restart count. No source SQL writes, migrations, seeds or role changes
were performed; the explicitly approved PostgreSQL startup naturally changes
physical files. This passes the 69.1 recovery gate, not an additive-upgrade
rehearsal or approval to execute 69.2/69.3.

Cleanup was verified at `2026-10-18T16:21:42Z`: task-owned container
`monitor-task057-452d70772a48` and volume `monitor-task057-452d70772a48-data`
were removed after exact identity/label/mount/network checks and a backup-hash
recheck. The source retained its ID and volume and was running/healthy; backend,
frontend and Mailpit remained stopped. The backup and byte-identical recovery
guide were retained. Exact resource identities are recorded in
[Task 057 results](../../agents/work/057-database-safety-audit/changes.md).

Retained backup directory, outside Git/OneDrive:
`%LOCALAPPDATA%/Monitor/backups/task057/20261018T161738Z-452d70772a48/`.
Its `monitor.dump` is 25,316 bytes, SHA-256
`3cc92a4cb840559c50f98409a52bef6e9c47114a20a897726f389c72c17fd959`.
Access is restricted to the current Windows user and SYSTEM; it is not encrypted.
Keep the private manifest/inventories and archive out of chat and Git. Logical
database backup does not include cluster role definitions/passwords or tablespaces;
matching ownership/ACLs in this isolated recovery does not establish global recovery.

For another isolated recovery, use the retained `RECOVERY.md` beside the archive:

1. Read `backup-manifest.json` privately; verify `monitor.dump` using
   `Get-FileHash -Algorithm SHA256`. Never overwrite this recovery set.
2. Follow the guide's PowerShell recipe using the manifest's pinned image,
   database and original role, a new labelled volume/container, `--network none`,
   no published ports and no application workers. Never mount the source volume.
3. Wait for the final server, then use binary `docker cp` and
   `pg_restore --exit-on-error --create` with a distinct control database and
   preserved ownership/ACLs. Do not pass the archive through text redirection.
4. Compare the target with private `reference.json`, including records, schema
   and both bookkeeping tables; advance sequences only in the disposable target.
   Verify exact target identities before cleanup, retaining backup/evidence.
   Sequence counters are non-MVCC; concurrent writes limit snapshot comparisons.
   None of this authorizes restoring over the development database.

Transition requirements retained from Task 057:

- Preserve all eight domain tables and **both** bookkeeping tables. The nine-domain
  target does not justify deleting historical bookkeeping.
- Retain exact auth digests/security state, IDs, numeric(12,3) ledger amounts,
  occurred_at/audit timestamps, unique constraints, FKs and identity sequence.
- Proposed conversion is additive: constrained users.type defaulting to user,
  plus user_meters with unique user/meter membership. Retain meters.user_id,
  current owner-name uniqueness/indexes, joins and API owner fields until sharing
  integration. Backfill owner memberships again at 69.4 cutover to include meters
  created by the interim owner-only app. Task 057 executed no conversion.
- Disable migration startup coherently with fresh initialization; do not run the
  old CREATE-table sequence against a new schema without its migration history.
  Keep existing bookkeeping as historical state, not data to silently delete.
- Existing-account admin assignment needs an explicit one-time reviewed update
  before DB roles are used. Fresh-only seeding is not an existing-volume upgrade.
  Redesign creator-delete cascades before enabling shared memberships.

### 69.2: Fresh bootstrap and explicit additive upgrade (Task 058)

Fresh/copy-upgrade and persistence verification passed; 64 backend checks passed
against current bind-mounted code in the cached backend image, whose installed
versions matched requirements. Both reload paths, source preservation and cleanup
passed. A network-disabled fresh backend build could not fetch uncached pip
requirements; no fresh build success is claimed. Uvicorn's development watch is
limited to `app/`, excluding research; production is unchanged.

The source's complete private inventory, container ID/start/restart count and
mounts were unchanged. At cleanup it was healthy on its existing volume; original
backend/frontend/Mailpit remained stopped. This does not approve a live upgrade,
role cutover or starting those stopped services.

Fresh initialization produced nine domain tables, two users/meters/memberships,
four balances and two top-ups, without fabricated migration history. The upgraded
copy has 11 physical tables: nine domain tables and both original bookkeeping
tables. Original-column record fingerprints, auth/ledger data, sequence and
existing catalog objects were preserved; all existing types defaulted to `user`,
with no promotion or seeds. Replaying the one-time upgrade failed without
changing the copy. Fresh restart/recreation retained its complete snapshot,
including a deliberately demoted seed admin; no seed replay re-promoted it.

Cleanup was verified at `2026-10-18T16:46:34Z`: only the six identity-checked
`monitor-task058-150c1a57666f-*` containers, three task volumes and internal
network were removed. Cached images were untouched. Task 057's backup/hash and
recovery guide remain; private Task 058 evidence is retained outside Git/OneDrive
under `%LOCALAPPDATA%/Monitor/backups/task058/20261018T163729Z-150c1a57666f/`.

`schema.sql` retains the original auth/ledger constraints, precision, times and
indexes. `user_meters` has `(user_id, meter_id)` primary key, cascading user/meter
FKs and a `(meter_id, user_id)` index. These are storage only, not shared access
or a last-member guard. Existing owner columns, name uniqueness and query/API
fields remain the compatibility bridge; redesign creator-delete cascades in 69.4.

Fresh-only `seed.sql` creates `hlabisasanele730@gmail.com` with DB type `admin`,
fictional `monitor-seed@example.test` with type `user`, two example meters, four
readings, two top-ups and owner memberships. It adds no credentials, sessions,
OTP codes or enabled reminders. Neither SQL file reruns on container recreation;
do not replay seeds to repair setup or grant a role. Runtime admins still come
from `MONITOR_ADMIN_EMAILS` until 059/69.3; seeded types are data, not proof of
active DB-based authority. Returning login/restart must not re-promote anyone.

On initialization failure, inspect the PostgreSQL log and exact volume/schema
state. A failed seed may leave an already committed schema and non-empty volume;
restarting does not rerun init scripts. Do not delete the volume, replay both
files or silently complete a partial setup. Preserve evidence/backup and agree
an explicit repair procedure first.

#### Applying an existing-database upgrade is a separate approval

`upgrade-058.sql` adds the same type/membership structure and backfills existing
owners. It preserves every old table/column and both migration histories; all
existing users default to `user`, without promotions or fresh seed replay.
It contains its own `BEGIN`/`COMMIT`, 5-second lock timeout and 60-second statement
timeout. It is an explicit one-time transition, not startup schema maintenance.

1. Obtain approval for the exact target and execution window. Verify current
   container ID, volume, database, PostgreSQL version and expected old schema;
   first make a fresh consistent backup and verify isolated restoration using
   the pinned image/private-manifest procedure above. A prior recovery pass
   does not prove a later source backup or upgrade is safe.
2. Rehearse the upgrade on that copy, not the source. Copy the SQL file into
   the verified target, then use `psql -v ON_ERROR_STOP=1 -f /path/upgrade-058.sql`
   with its explicit database/role. Do not wrap the file in another transaction,
   run schema.sql/seed.sql or disable errors. Failure must leave no partial upgrade.
3. Compare original-column records, IDs, auth/ledger state, sequences and both
   histories against the backup; separately validate type defaults, constraints
   and owner memberships, plus existing owner-scoped API behavior.
4. Only after separate live approval and repeated target/backup checks, execute
   that reviewed transaction on the intended source. Never reset or restore over
   it automatically. A failed rehearsal is not permission to alter the source.

Repeat owner-to-membership backfill at 69.4 cutover to include meters created by
the interim owner-only app. Explicit existing-account role mapping and removal
of admin-env authority remain separately approved 059/69.3 work.

Tariffs, Rand amounts, hardware/OCR data and forecast-model adoption remain out
of scope. Never commit service volumes, database dumps or private customer data.
