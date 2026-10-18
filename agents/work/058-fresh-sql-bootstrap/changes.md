# Task 058: Fresh SQL bootstrap

## Result and implementation

Completed Ticket 69.2 for fresh setup and an isolated-copy upgrade rehearsal.
The user explicitly chose copy-only; the current database was not upgraded,
seeded, reset or restarted. Task 059 / DB-only administrator authority still
needs its own prompt/approval and current-volume transition decision.

- Added schema.sql: nine domain tables, preserving all eight historical tables'
  SQL contracts and indexes, plus constrained users.type default user and
  user_meters PK/FKs/reverse index. Owner columns/name uniqueness remain.
- Added fresh-only seed.sql: approved hlabisasanele730@gmail.com DB-admin and
  separate fictional monitor-seed@example.test owner, Seed home/Seed shop,
  four balances and two top-ups. Their ledger rates are 10/5 kWh/day; they are
  not household evidence. No auth credentials/sessions or reminder rows seeded.
- Added upgrade-058.sql: one explicit transaction with lock/statement timeouts,
  additive type/membership structure and owner backfill only. No seed replay,
  existing-user promotion, deleted state or historical-migration rewrite.
- Compose mounts read-only 01-schema.sql then 02-seed.sql for PostgreSQL empty
  volume initialization. Removed backend migration command/mount; the named
  source volume, environment configuration and frontend polling remain.
- Kept eight historical SQL files and inactive app.migrations. Its guard rejects
  the new users.type schema before any migration-bookkeeping write. Retired
  integration initialization calls; schema checks now exercise the bootstrap.
- Development Docker CMD retains reload but watches app/ only. The isolated
  full-tree StatReload check stalled scanning the research environment at about
  90% CPU; this small startup adjustment made app reload work without scanning
  research dependencies. Production CMD, app APIs/UI and forecasting are unchanged.
- Updated root/component READMEs and context; 69.1 target acceptance and 69.2
  fresh/copy verification are complete. Future role/sharing/reminder work is not
  activated. The approved SQL-focused review-size exception was used.

## Verification actually performed

- Independent normalized comparison matched all eight historical SQL migrations
  exactly after excluding only approved additions and fresh transaction/schema
  wrapping: security checks, NUMERIC precision, UTC-aware times, FK/index contracts.
- Fresh PostgreSQL 17.11 on a labelled dedicated volume initialized both files:
  nine domain tables, two users/meters/memberships, four balances, two top-ups,
  no reminders and no fabricated migration bookkeeping.
- All **64 backend checks passed** in 5.57 seconds using an explicitly isolated
  database URL and internal-only Mailpit. Coverage includes OTP/cookie sessions,
  owner/admin CRUD/search, balances/top-ups/dashboard/forecasts/reminders, new
  type/membership constraints and legacy-runner refusal without history writes.
- Initial run: 63 passed, one failed because an existing admin-list assertion
  assumed an empty database. Corrected it to compare the exact baseline mapping
  plus fixture meters, retaining strong global-access/isolation checks. Rerun
  passed all 64; no application access rule was changed to satisfy the test.
- Used the retained verified Task 057 archive after rechecking its SHA-256.
  Restored without stripping ownership/ACLs into a networkless separate volume;
  the restored inventory exactly matched its private snapshot reference.
- Applied upgrade-058.sql to that copy only. All original-column record counts/
  private fingerprints matched, including IDs, auth digests/security state,
  ledger amounts/times and both migration histories. Original catalog entries
  and identity sequence state were retained. New memberships matched all four
  existing owners/meters; all existing user types were user, with no promotion.
  Eleven physical tables: original eight domain plus membership and two histories.
- Attempted duplicate upgrade on the copy: it failed as expected; the complete
  post-failure inventory was unchanged. No automatic retry/reset mechanism added.
- After checks, manually demoted only the fresh test seed-admin. Full private
  inventories matched through isolated PostgreSQL restart and container recreation
  using the same test volume; no seed duplication, role re-promotion or data replay.
- Both development watchers reloaded changed timestamps with byte-identical source
  contents: backend app/ StatReload and frontend Vite polling. Tests used the
  actual development CMD parsed from the updated Dockerfile, with no host ports.
- Parsed actual Compose configuration privately: ordered read-only init mounts,
  no backend migration command/mount, persistent original volume name unchanged.
- Read-only source inventories matched before/after; original container ID,
  start time, restart count and mounts matched. Original frontend/backend/Mailpit
  stayed exited. No protected source sequence or SQL write was executed.

## Limits, evidence and cleanup

A network-disabled fresh backend-image build missed its dependency cache and
failed during pip installation. Tests instead used the existing development
image with current bind-mounted code; direct dependency-version checks matched
every pinned runtime requirement. No new image build success or dependency
installation is claimed. No production build or UI test-suite rerun was needed
for unchanged production/UI behavior; development startup was exercised above.

The first task-helper resume regenerated a label token for its exited test
container. Guarded resume detected the mismatch before deleting anything;
the exact recorded ID, task label, network and source-volume exclusion were
independently checked before removing only that container and fixing the helper.
An initial reload timeout was diagnosed and resolved by app-only watching.
These were temporary verification-tool failures, not source data mutations.

Private evidence is retained, ACL-restricted and not encrypted, outside Git and
OneDrive at:
C:\Users\hlabi\AppData\Local\Monitor\backups\task058\20261018T163729Z-150c1a57666f.
It includes original-source/fresh/upgrade inventories, original-column comparison,
test/dependency logs, resource identities, verification and cleanup summaries.
The Task 057 archive/hash and RECOVERY.md remain retained; this rehearsal does
not authorize overwriting the source or supply a cluster-global backup.

Cleanup verified at 2026-10-18T16:46:34Z. Removed only exact-ID/task-token checked
resources with prefix monitor-task058-150c1a57666f-:

- six final containers: frontend, backend, tests, mailpit, upgrade, fresh;
- three volumes: fresh-data, upgrade-data, node-modules; and
- one internal network: network.

Earlier replacement test/backend/fresh containers were likewise identity checked
before removal. Full final IDs are retained privately in cleanup-summary.json.
No task-labelled containers/volumes/networks remain. Reused images, original
source volume and recovery archive were not removed. Disposable database copies
can be rebuilt from the retained archive/SQL; they were not unique source data.
Post-cleanup source DB is healthy; its other three services remain stopped.

## Reuse and handoff

Reused raw SQL, Psycopg APIs, Docker targets/images, existing backend checks,
Task 057's PostgreSQL snapshot inventory/recovery approach and native PG tools.
Only ignored task-local helpers and the existing local Python environment were
needed; no runtime dependency, backup daemon or extra permanent service.

Fresh init is once per empty volume, not idempotent maintenance. Schema and seed
commit separately; a failed seed needs explicit diagnosis/repair, not volume
deletion or automatic replay. A later live upgrade needs a new backup, isolated
rehearsal and exact-target approval. Existing-admin mapping/env removal belongs
to 059; membership authorization/creator-delete safety and repeat owner backfill
belong to sharing cutover. No real email, source reset/write, sibling change,
forecast change, commit or push occurred.

Final checks passed: git diff --check, explicit new-SQL/work-record whitespace,
all 31 local Markdown links across changed docs/work records, ignored-helper
checks and exact changed/untracked file scope. Historical migrations, frontend
content, .env.example, refocus.md and unrelated runtime files have no diffs.
Only the intentional legacy CLI guard and development watch scope changed in
backend implementation. Existing Git LF/CRLF/global-ignore warnings remain
non-blocking. Final Docker metadata confirmed source healthy/other services
stopped and no Task 058 containers, volumes or networks remaining.
