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

OTP signup creates a user after verification; Task 063 sharing may provision a
regular account first without granting authentication. Plaintext OTPs/tokens are
never stored. Only users.type grants admin access, without env/email fallback. Fresh
seeds provision hlabisasanele730@gmail.com as admin and monitor-seed@example.test
examples, without credentials/sessions or enabled mail. Login/restart never
overwrites manual role changes; see the [backend README](../backend/README.md).

Meter names are case-insensitively unique per owner. Balances have unique
per-meter occurrence times; purchases may share a time. Store UTC instants,
preserving occurrence times separately from audit times. Rates/forecasts are
derived, not stored truth. Task 063 code uses current membership/admin access,
with transactional last-member guards. Fresh schema restricts creator/member-user
deletion, while explicit whole-meter deletion retains history/member cascades.
Task 064 applied these FK changes to the current development DB after fresh
backup/restore/rehearsal verification. The later user-started stack passed
read-only checks and remains running; do not replay the transition.
No account-delete API is added.

## Earlier recovery (Task 059)

Retained pre-upgrade recovery set, outside Git/OneDrive:

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

## Earlier recovery and copy-only gate (Task 063)

A fresh current-data snapshot and exact restore are verified at
%LOCALAPPDATA%/Monitor/backups/task063/20261018T190432Z-f9f5d7fc8a08/.
Its monitor.dump is 27,606 bytes; SHA-256
396253f7be8b5ea974956b3a60f88fce7872e9b3ccd5838d51dba8aaff19558e.
Private inventories, RECOVERY.md and reviewed SQL/schema are retained with
user/SYSTEM-only ACLs, not encryption. Never commit or publish the private set.

Unlike the earlier 059 backup, this already contains DB roles and memberships.
Rehearse only Task 063's reviewed FK/backfill transaction for this baseline,
not upgrade-058.sql, the earlier admin assignment or fresh seeds. Matching SQL
is versioned under agents/work/063-shared-meter-backend/upgrade.sql and privately
retained as reviewed-upgrade.sql (SHA-256
88a9339a489c48df857b5580e154be4f91bc773dfeb9ca9eaf5c7aafa469bb1e).

The copy rehearsal preserved every record/role/sequence and both histories;
only the two intended FK deletion actions changed. Fresh/copy definitions match.
Backfill repairs memberless interim meters without re-adding departed creators.
Current-code read-only checks on the clone passed. The three owned containers
and two volumes were removed; source inventories/metadata remained unchanged.
Details and limits are in [Task 063 results](../../agents/work/063-shared-meter-backend/changes.md).
This is not approval to run the transaction or start apps on the current volume.

## Latest recovery and live transition (Task 064)

The separately approved transaction was applied once and verified at
2026-10-18T19:45:25Z,
after fresh full-backup/exact-restore rehearsal and final source-preservation
checks. It changed exactly two user FK actions to RESTRICT; zero membership
backfills were needed. All original records, roles, auth state, sequences and
both history tables match the rehearsed state. PostgreSQL was not restarted.

Retained private recovery set, outside Git/OneDrive:

    %LOCALAPPDATA%/Monitor/backups/task064/20261018T194005Z-2730c044ddfe/

monitor.dump is 27,606 bytes; SHA-256
9a3c3d83b5c4ca8edf1b176b19f68741d01b0db636cf4a1d1b074a44d0fc07c1.
It includes RECOVERY.md, frozen reviewed SQL/schema and private before/rehearsed/
live inventories and execution evidence, restricted to the user/SYSTEM, not
encrypted. The reviewed SQL/schema hashes match Task 063 above. The dump is the
pre-064 state; restore/rehearse only on an isolated copy under an approved plan.
Never automatically overwrite the current volume or replay seeds/role assignments.

The initial Docker health gate failed; the bounded backend-only diagnostic then
passed unchanged and stopped again, with independent full-inventory preservation
checks. The user subsequently restarted PostgreSQL on the same volume and
rebuilt/started the full app. Current read-only checks confirm both user FKs use
RESTRICT, five meter-child FKs retain CASCADE, all nine domain tables and both
histories remain, roles persist and no orphaned/memberless meters exist.
All services remain running; the final verification performed no service actions
or DB writes. Do not rerun the committed SQL as a startup repair. See
[Task 064 results](../../agents/work/064-shared-backend-activation/changes.md).

## Remaining database/access work

The [root roadmap](../../README.md) owns stable IDs and priority; the
[backend](../backend/README.md) and [frontend](../frontend/README.md) define detail.

- 69.1-69.3: recovery, fresh bootstrap and DB-only roles are complete.
- 69.4: shared authorization, preserved-data FK transition and running-stack
  read-only smoke checks are complete in Tasks 063/064.
- 69.5: membership-aware sharing UI/My/All/search is complete in Task 065.
- 69.6: strictly-next UTC 1st and actual calendar-month quantities, separate from
  predicted run-out, are complete in Task 066.
- 69.7: 09:00 UTC on month-end to current meter members, including newly shared
  users, not all accounts. Discover only the latest missed cycle; retry all saved
  pending work. Task 068 completes the finite monthly pass using the existing
  delivery schema; all 134 isolated backend checks and real Mailpit SMTP checks
  pass, without source SQL or scheduler activation. Preserve
  legacy rows and low-balance behavior; reconcile legacy backlog/keys and persist
  a fixed activation cutoff before separately approved activation in 69.7.2.
- 70: HTML email with plain fallback/trusted links after reminder rules.

Keep separate reminder preferences/claims, digest-only security and occurrence
times. Add no tables/triggers/procedures without need. Cleanup does not authorize
a live transition/reset, sharing activation, seed replay or future feature.
