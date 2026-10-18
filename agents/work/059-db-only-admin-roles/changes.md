# Task 059: DB-only administrator roles

## Result: complete

The user approved the implementation prompt and the current-DB upgrade after
fresh backup/rehearsal, promoting only the existing approved admin account.
The approved plan required app writers to remain stopped. Read-only preflight
instead found all four Monitor services running with recreated container IDs.
The user then explicitly approved stopping only frontend/backend/Mailpit, leaving
PostgreSQL running. Those three were stopped once and remain off. After the
fresh verified backup, rehearsal and isolated checks below, the approved schema
and one-time role transactions were applied; no database restart/reset occurred.

Current source: monitor-dev-database-1, ID
06438f44071a29fb405b6afc8569e1dcaa575b3c23163b0fcd3f75c7f658dd4e;
volume monitor-dev_postgres-data; PostgreSQL 17.11, image
sha256:b0f9560a2de083e2cc7382e75f808c7381a32852a7ec49117deedb300e552b24.
Initial REPEATABLE READ READ ONLY preflight confirmed ten physical tables, no
users.type and exactly one approved existing account, without exposing rows.
The initial running bind-mounted app could reload queries before its schema
transition; that mismatch is now resolved by the verified upgrade. No live HTTP
login was performed: the source app services remain stopped by agreement.

## Implemented scope

- Added stored type to User and existing OTP/session queries; no extra role
  query, cookie-role cache, email match or startup promotion. New signup still
  INSERTs email only/default user; returning login preserves stored type.
- Auth responses/dependency derive is_admin from type == admin. Public API shapes,
  session security and existing owner/admin meter scopes remain unchanged.
- Removed administrator configuration from settings, Compose and both committed
  env examples. Removed only that setting from ignored software/.env via
  apply_patch; normalized unrelated-setting fingerprints matched. No credentials
  or file contents were printed. No software/backend/.env exists.
- Updated tests for DB-admin fixtures, same-cookie promote/demote access,
  returning OTP/manual demotion and negative stale-env/email override cases.
- Updated relevant READMEs/context/roadmap with verified results and recovery
  limits; Ticket 69.3 is complete. Historical 057/058 results remain historical.

## Reuse and checks

Reused User, OTP/session queries, authenticated-user dependency and meter scopes,
Psycopg, existing test suite and the retained 058 schema/upgrade path. No new
dependency, service, schema file, model, UI or sharing integration was added.
Independent read-only runtime review found no code blocker or OTP/session-policy
regression. There is no new dependency, runtime schema-maintenance function or
permanent backup service. Production implementation remains under 100 changed
lines; tests/docs excluded. Actual verification and cleanup follow.

## Verification and live transition

- All **68 backend checks passed in 9.34 seconds** against an explicitly isolated
  fresh PostgreSQL/Mailpit target using current read-only bind-mounted code.
  Installed dependencies matched all six requirement pins in the existing image.
  No fresh image build or dependency installation was required or claimed.
- Covered signup/default user, returning OTP/manual demotion, same-session
  user/admin/user changes affecting /api/me and foreign-meter access on the next
  request, global admin CRUD and ordinary-user isolation. Existing cookie,
  digest/expiry/revocation, ledger/dashboard/forecast/reminder checks passed.
  Three legacy env-key references remain only in negative regression tests.
- After the separately approved app stops, held a REPEATABLE READ READ ONLY
  exported snapshot for a complete custom-format pg_dump --create and matching
  private all-table inventory. No source sequences were advanced by verification.
- Restored that NEW archive to a task-labelled networkless PG17.11 container,
  separate volume, no host ports/workers; original ownership/ACLs and full
  inventory matched the reference. Rehearsed upgrade-058.sql's own transaction,
  then a separate bounded role transaction requiring exactly one existing
  regular account. No source seeds, inserted users or auth fixtures were used.
- Compared every original-column record privately, IDs/auth state, ledger
  numeric values/times, catalog objects, sequence state and both histories.
  Checked new memberships and exact admin-only mapping separately. A read-only
  current-code check against this copy also passed without source access.
- Before live writes, rechecked quiet services, source ID/image/start/restart
  count/mount set, complete original inventory, backup SHA-256 and reviewed SQL
  hashes. The first attempt stopped BEFORE any write because Docker reordered
  the otherwise identical mount array; exact mount-set comparison fixed that
  false positive without dropping any mount fields or target checks.
- Applied the same two reviewed transactions to the source at
  2026-10-18T17:21:00Z. Afterward, all original projections/state were preserved,
  and the complete live inventory equalled the verified rehearsal. Exactly the
  existing hlabisasanele730@gmail.com account is admin; the other user is user.
  Source ID/start/restart count/image/mount set are unchanged; DB is healthy.
- Later independent review recommended freezing SQL bytes before execution.
  The temporary helper was hardened for future runs; it was NOT rerun. The
  completed operations used unchanged reviewed files and matching hashes/live
  inventory; no retroactive frozen-byte guarantee is claimed.

Final counts: users 2, meters 4, user_meters 4, balances 7, top-ups 4,
OTP challenges 16, sessions 16, reminder settings/deliveries 0;
monitor.schema_migrations 8 and public.schema_migrations 1. Eleven physical
tables; no domain table/history was dropped. Rates remain derived per meter.

## Retained recovery and cleanup

Private directory:
C:\Users\hlabi\AppData\Local\Monitor\backups\task059\20261018T171408Z-4fbf46c4c3c5.
It is outside Git/OneDrive, ACL-restricted to the Windows user and SYSTEM and
not encrypted. monitor.dump is 25,316 bytes, SHA-256
a14acd1536b5e7aa04c66a774c3baa5738ad5060e47a02310f8ad940f5524cd1.
Retained: manifest, reference/rehearsal/source-after inventories, RECOVERY.md,
reviewed SQL, test/dependency logs, resource identities and stage/cleanup proofs.
No customer row contents/digests or credentials are in chat/Git. Earlier backups
were retained. This logical backup excludes cluster roles/passwords/tablespaces;
restoring its old schema is not authorization to overwrite newer data or replay
the one-time admin mapping. Quiet writers support the sequence-state comparison.

Removed only identity/label/network/mount checked task resources, prefix
monitor-task059-4fbf46c4c3c5-:

- fresh, mailpit and tests containers; fresh-data volume; internal network
  (test cleanup verified 2026-10-18T17:16:11Z);
- upgrade and code-check containers; upgrade-data volume
  (final cleanup verified 2026-10-18T17:22:38Z).

Full IDs are retained privately in cleanup-tests.json/cleanup-transition.json.
No Task059 containers, volumes or networks remain; cached images and source
volume were not removed. The copies were reproducible from fresh SQL/retained
backup, not unique source data. Source DB remains healthy and the three source
app services stay off; starting them requires user direction.

## Handoff

No source OTP/session writes, account creation, seed replay, email, automatic
upgrade/promotion, source reset/restart, UI/model/sharing change, sibling change,
commit or push occurred. Live schema/type/membership backfill and the explicitly
approved one-time assignment were the only source SQL mutations. New shared
authorization/last-member/creator-delete handling remains Task060/Ticket69.4,
requiring questions and a separate approved prompt. No frontend test rerun or
source HTTP-login check is claimed; the public API/UI shapes are unchanged.
Final checks passed: git diff --check, explicit work/docs whitespace, all 32
local Markdown links, active-code/config/example admin-env scan (no matches),
and exact modified/untracked scope. Only 059 work records are untracked; local
env and verification artifacts are ignored. UI, model, Dockerfile, schema/seed/
upgrade-058 files, historical SQL and refocus.md have no diffs. Existing Git
LF/CRLF/global-ignore warnings remain non-blocking. Final read-only preflight
confirmed eleven tables/users.type present and the same source ID/volume;
Docker metadata confirmed healthy DB, three stopped app services and no task
containers/volumes/networks. No Git write operation was performed for 059.
