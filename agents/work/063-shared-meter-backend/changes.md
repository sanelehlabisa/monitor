# Task 063: Shared-meter backend

## Status

Approved implementation, isolated verification and owned-resource cleanup are complete.
The original task excluded Git writes; the user subsequently approved its Git
handoff to master. Live SQL transition and source activation still need their
separately reviewed task approval.

## Implemented and reused

- Reused the existing user_meters table, DB roles, raw SQL and cookie/OTP flow.
  Meter creation atomically creates its initial membership. All protected meter,
  nested ledger/dashboard/reminder paths now use membership or global admin scope.
- Added GET/POST /api/meters/{id}/members and DELETE /members/{user_id}; member
  results contain only user_id/email. Sharing normalizes/validates email and
  idempotently provisions a missing regular user. It never overwrites roles,
  creates a session, bypasses OTP or exposes a global account directory.
  A failed sharing transaction rolls back its newly provisioned account.
- Any current member/admin may permanently delete the meter/history. Leaving
  removes membership only. Parent-row locks followed by separate access checks
  serialize member changes, meter/ledger writes and dispatch; admins cannot
  remove the last member either. SQL member-email search returns each meter once.
- Creator fields/name uniqueness remain compatible metadata, not permission.
  No frontend source/controls or forecast math changed. Sharing/admin My UI is
  future 69.5; source data activation is a separate gate under 69.4.
- Legacy reminders still require opt-in and target the creator only while they
  are a current member. Dispatch skips stale candidates, rechecks before SMTP
  under the parent lock and retains existing dedupe/retry behavior. SMTP is not
  transactional; crash/retry exactly-once delivery is not claimed.
- Fresh schema restricts creator/member-user deletion; whole-meter cascades stay.
  No account-delete API, transfer flow, trigger, role, service or dependency added.
  Reviewed upgrade.sql stays under this work directory, not runtime startup SQL;
  database/ still has schema.sql, seed.sql and README.md only.
  Backfill repairs only memberless interim meters, never restores a departed
  creator on an otherwise shared meter. Actual rehearsal needed zero backfills.
- Updated current README/context contracts for sharing-provisioned users and
  settled permissions; historical results and deferred work are preserved.

## Source-service authority and preservation

Task 063 preflight found all services running again. The user separately approved
stopping only frontend/backend/Mailpit and keeping PostgreSQL running. Root
verified exact names/identities and stopped only those three; they remain off.

Source database: monitor-dev-database-1, ID
06438f44071a29fb405b6afc8569e1dcaa575b3c23163b0fcd3f75c7f658dd4e,
volume monitor-dev_postgres-data, pinned PostgreSQL image
sha256:b0f9560a2de083e2cc7382e75f808c7381a32852a7ec49117deedb300e552b24,
start 2026-10-18T18:28:38.720652838Z and restart count 0. This start precedes 063;
it differs from the earlier tasks' historical metadata. No source SQL writes,
schema changes, seed replay, account/role edits or database restart occurred.

## Backup and copy-only rehearsal

- New complete held-read-only-snapshot dump retained outside Git/OneDrive:
  %LOCALAPPDATA%/Monitor/backups/task063/20261018T190432Z-f9f5d7fc8a08/monitor.dump.
  Size: 27,606 bytes; SHA-256
  396253f7be8b5ea974956b3a60f88fce7872e9b3ccd5838d51dba8aaff19558e.
  User/SYSTEM-restricted ACL, not encrypted. RECOVERY.md, reviewed SQL/schema and
  private inventories/evidence remain beside it; never publish private records.
- Upgrade SQL SHA-256:
  88a9339a489c48df857b5580e154be4f91bc773dfeb9ca9eaf5c7aafa469bb1e.
  Fresh schema SHA-256:
  24c4fc6e8ec59307b8f82aa95427e2a57cf286c93cf82172ab9403c144c7c249.
- Exact restore matched all data, roles, catalog objects, sequences and both
  monitor/public schema_migrations histories. Rehearsal changed exactly two FK
  actions and preserved original records/roles/sequences. Fresh/upgraded domain
  columns, constraints and indexes match; historical tables remain on the copy.
- Copy account deletion failed with SQLSTATE 23503 without losing shared history. Synthetic
  checks verified membership-user deletion rejection, whole-meter cascades and
  narrow backfill without regranting a creator who left. No extra tables needed.
- Read-only before/after source inventories and ID/image/start/restart/mount
  metadata match. Source counts remain 2 users, 4 meters/memberships, 7 balances,
  4 top-ups, 16 challenges, 16 sessions and empty reminder tables; both histories
  retain 8/1 rows. Safe summary: .tmp/task063/db-summary.json.
- Current-code read-only clone checks passed: six dashboard calculations match
  the single forecast boundary (five available/one insufficient), member/admin
  scopes and ten foreign-read rejections verified. No fixture or auth writes;
  default/actual transaction read-only mode was enforced. Full fresh/copy domain
  definitions, ownership/ACLs and sequence definitions match as well.
- At 2026-10-18T19:10:52.980575Z, three exact-owned containers and two volumes
  were removed after backup/SQL hashes, proof, ID/label/mount/network/source guards.
  A first guard rejected Docker Desktop's Linux-normalized private-drive path
  before deletion; it was corrected to accept only the two exact equivalent
  Windows/Linux paths, not a broad match. No networks/images/source resources
  were changed; backup/evidence remain. Proof: .tmp/task063/cleanup-db.json.

## Backend verification and limits

- Final fresh isolated backend/Mailpit suite: 90 passed in 35.77 seconds, no warnings.
  Covers all 21 protected method/path pairs, OTP, member/admin CRUD, provisioning,
  preserved roles, concurrent signup/sharing, rollback, last-member protection,
  11 lock-blocked mutation variants, scoped search and removed-creator reminders.
  Cached backend dependencies match all six requirements pins; no fresh image
  build or live/browser end-to-end validation is claimed.
- Two prior runs found fixture-only issues: 85 passed/one failed because HTTP
  correctly withheld a Secure login cookie; the test client now uses HTTPS.
  Then 89 passed/one failed because a cross-meter fixture reused a unique creator/
  name pair; it now includes the actor ID. No runtime security/validation weakened.
- Canonical OpenAPI comparison adds exactly three member operations and
  MemberResponse. Existing request/response contracts are unchanged; only two
  operation descriptions changed. SHA-256:
  3258dd03ab299c1e93e8cb97cfb4dd360c8a5256a7ea97bec4d3357b50bf24f9.
- All three runs' exact owned resources were removed: nine containers, three
  volumes and three networks, with final cleanup verified at
  2026-10-18T19:15:42.904408Z. Images and source resources were untouched.
  Together with the database rehearsal, cleanup removed 12 containers, five
  volumes and three networks. Recovery dumps and private evidence are retained;
  isolated resources can be recreated. Final safe test summary:
  .tmp/task063/summary-063-5d6ce2c94784.json. Restricted evidence:
  %LOCALAPPDATA%/Monitor/backups/task063/20261018T191403Z-063-5d6ce2c94784/.
- Python parsing, local Markdown links and whitespace checks passed. Forecast,
  frontend source, research, hardware, refocus.md, dependency manifests and Compose
  remain unchanged. Final source metadata matches the recorded identity/start/
  restart/mount; PostgreSQL stays healthy/running and the three apps stay stopped.
- Source FK/backfill activation and live HTTP/end-to-end testing remain future;
  passing fresh/copy checks does not authorize starting current-volume services.
  No real mail, UI redesign or research/hardware/refocus edits. No Git writes
  occurred during implementation; the subsequent handoff has separate approval.
- The approved implementation-size exception covers coherent authorization,
  provisioning, concurrency and FK safety plus necessary mechanical call-site
  changes; tests/docs are excluded. Actual implementation: 337 added/117 removed
  lines (454 total, including new membership module and reviewed SQL), within
  the approved 350-500-line estimate. No added abstraction or dependency.

## Git handoff

The user approved committing/publishing the completed work to master and starting
the next task's preparation. The worktree is already on master, so no branch
merge or force push is needed. The 90-check result above remains the verified
implementation result; handoff checks do not claim a new live test run.
