# Task 064: Activate Shared-Meter Backend

## Status

Complete within approved scope: the live DB transition, isolated backend checks
and read-only running-stack smoke checks passed. Ticket 69.4 is complete;
sharing UI remains 69.5. Initial failed startup and the successful bounded
diagnostic below are historical. The user subsequently started the full stack
and authorized testing/commit/push. Final verification leaves it running and
does not create live fixtures, OTP/session writes, real mail or service actions.

## Context and reuse

- The user approved publishing completed Task 063 to master and starting the
  next task. It was already on master; no merge commit or force push was needed.
- Commit 59e7e205488e9d3965a4a1f5081c127381778643 was pushed to origin/master.
  Fetch/review found no remote divergence. Only the 38 reviewed implementation,
  test and documentation files were committed; private backups/.env/.tmp remain
  excluded. Staged whitespace checks passed. The 90 checks recorded under 063
  were not rerun for this Git-only handoff; no new runtime-validation claim.
- Inspected current instructions, roadmap, software/database READMEs, schema,
  reviewed transition SQL, backend startup, Compose and existing work records.
  Reuse Ticket 69.4 rather than creating a duplicate roadmap ticket.
- The user chose to start the three existing app services after backup, rehearsal
  and successful transition verification; PostgreSQL remains running. This is
  incorporated into the prompt, which the user subsequently approved.

## Checks and limits

Preparation performed no live SQL, service actions, backup or application code
changes. Implementation results follow below as their gates complete.
Preparation document links/whitespace passed. Independent read-only plan review
clarified identical frozen SQL bytes, current-code container mounts/commands and
stopping only task-started apps if startup checks fail.

## Implementation preflight

- Exact source ID/image/volume/start/restart count match Task 063's recorded
  baseline; PostgreSQL is running/healthy. Backend/frontend/Mailpit are exited.
  Commands and bind mounts serve the committed Task 063 code; tracked app/Compose/
  schema files are unchanged from master 59e7e20. No implicit rebuild/recreation.
- Fresh private backup/copy rehearsal and fresh isolated backend checks ran
  independently. Neither worker wrote source data or started/stopped source
  services. Root alone executed the later approved live transaction/start attempt.

## Fresh isolated backend verification

- All 90 checks passed in 49.95 seconds, without warnings, against fresh synthetic
  PostgreSQL/Mailpit resources. API bytes and all six dependency pins exactly
  match approved Task 063; no code or dependency changes were needed.
- OpenAPI SHA-256:
  3258dd03ab299c1e93e8cb97cfb4dd360c8a5256a7ea97bec4d3357b50bf24f9.
  Verification made zero source queries/actions and sent only isolated mail.
- At 2026-10-18T19:38:06.879224Z, the exact three owned test containers, one
  volume and one internal network were verified removed; images untouched.
  Evidence remains at %LOCALAPPDATA%/Monitor/backups/task064-tests/
  20261018T193540Z-064-ab39ed4cea7f/. Safe proof:
  .tmp/task064-tests/comparison-ab39ed4cea7f.json.

## Recovery and isolated rehearsal

- Retained full held-read-only-snapshot backup outside Git/OneDrive:
  %LOCALAPPDATA%/Monitor/backups/task064/20261018T194005Z-2730c044ddfe/monitor.dump.
  Size 27,606 bytes; SHA-256
  9a3c3d83b5c4ca8edf1b176b19f68741d01b0db636cf4a1d1b074a44d0fc07c1.
  User/SYSTEM-only ACLs, not encryption. RECOVERY.md, frozen reviewed SQL/schema,
  private inventories and execution/diagnostic evidence remain beside it.
- Frozen SQL from commit 59e7e205488e9d3965a4a1f5081c127381778643:
  SHA-256 88a9339a489c48df857b5580e154be4f91bc773dfeb9ca9eaf5c7aafa469bb1e.
  Fresh schema SHA-256:
  24c4fc6e8ec59307b8f82aa95427e2a57cf286c93cf82172ab9403c144c7c249.
  The identical frozen bytes were used in rehearsal and live execution.
- Exact restore preserved all 11 physical tables, stored types/auth state,
  sequences and both histories. Rehearsal changed exactly two user FK actions;
  zero backfills were needed. Synthetic copies verified memberless-only backfill,
  departed-creator exclusion, account-delete rejection and meter-child cascades.
  Fresh and upgraded domain catalogs/ownership/ACLs match.
- Docker reordered Mounts in its inspect output, causing a safe final metadata
  assertion halt before any live write. Every mount field/value was identical.
  Only enumeration order was canonicalized; the failed assertion location and
  completed preceding checks were confirmed privately. A read-only resume
  reverified source/reference, copy/rehearsed, records/roles/histories/sequences,
  intended FK/membership changes and archive/committed hashes. No fixtures replayed.
- Pinned current-code read-only checks on the upgraded copy passed six dashboard
  comparisons (five available, one insufficient), ten foreign-read denials and
  member/admin scopes. No new auth or record writes. Final pre-live gate passed
  at 2026-10-18T19:44:32.594788Z; root repeated it immediately before live SQL.
  Safe results: .tmp/task064/db-summary.json and prelive-gate.json.

## Live transition and failed activation

- Root executed the approved frozen BEGIN/COMMIT transaction once with
  ON_ERROR_STOP and its existing timeouts, after final exact-source preservation
  checks. An exclusive private attempt marker prevents accidental retry; timeout/
  unknown commit outcomes would require review, never automatic replay/restore.
- At 2026-10-18T19:45:25.849593Z, all live rows, roles, auth state, sequences and
  both history tables exactly matched the rehearsal. Only two FK actions changed
  to RESTRICT; zero membership backfills, seed replays or role/account changes.
  No database restart/recreation. Safe result:
  .tmp/task064-activation/live-summary.json.
- After exact container/command/bind/network/loopback guards, root started only
  existing Mailpit then backend. Backend app startup completed at
  2026-10-18T19:46:12.576873Z, about 22.2 seconds after its container started.
  No import/configuration/bind exception or app crash was observed.
- Docker's health command repeatedly hit its 3-second execution timeout, even
  after application startup. The 55-second health-wait deadline expired before
  direct HTTP checks or frontend startup. A longer global wait alone is not a
  demonstrated fix; compare direct host HTTP and in-container probe timings in
  a separately approved bounded retry before changing settings.
- The failure guard stopped only task-started backend/Mailpit. Backend shut down
  cleanly (exit 0); frontend was never started. At
  2026-10-18T19:46:45.634583Z, stopped-app verification passed with no rollback
  failures. No dependency/config/app changes, source fixtures/OTP sessions, real
  mail or reminder runs. No live HTTP/login/browser success is claimed.
  Safe result: .tmp/task064-activation/services-summary.json. Logs, health timing
  and classified diagnosis are retained privately, never published in Git.

## Final preservation and cleanup

- Independent read-only verification after the failed start and again after
  cleanup matched the complete rehearsed/live inventory. Source counts remain
  2 users, 4 meters/memberships, 7 balances, 4 top-ups, 16 challenges, 16 sessions,
  empty reminder tables and 8/1 history rows. PostgreSQL remains healthy on the
  same ID/image/volume, start 2026-10-18T18:28:38.720652838Z and restart count 0.
  All three exact app containers are exited.
- Cleanup at 2026-10-18T19:49:03.154551Z removed only three rehearsal containers
  and two dedicated volumes after exact-ID/label/mount/network, backup/hash and
  post-live preservation guards. Together with tests, six disposable containers,
  three volumes and one network were removed; no images/source resources removed.
  Disposable resources can be recreated; recovery dumps and evidence remain.
  Safe proofs: .tmp/task064/cleanup-db.json and postlive-readonly.json.
- README/context now distinguish the completed DB transition from incomplete app
  activation. SQL must not be replayed to repair startup. Sharing UI, forecast
  changes and other tickets remain unimplemented. No new Git handoff.
- Final local links and whitespace passed across nine active/task documents;
  git diff --check passed. Protected app/tests, schema/seed, Compose, dependency,
  frontend, research, hardware and refocus files have no diff from master.
  No changes are staged. Startup diagnosis and live/helper safety received
  independent read-only review; another restart requires recovery direction.

## Approved bounded diagnostic continuation

- Reused existing container/command/bind/loopback guards. The user explicitly
  approved one diagnostic restart; only the existing backend was started.
  Mailpit/frontend stayed off; PostgreSQL was never restarted or recreated.
  The diagnostic used process-only anonymous /health GETs, not login/OTP,
  authenticated data requests or the reminder runner.
- Fresh independent read-only baseline at 2026-10-18T19:59:36Z matched the
  complete verified live/rehearsed state. The measured run finished at
  2026-10-18T20:02:04.399299Z in 14.661 seconds; backend started at
  2026-10-18T20:01:50.880840311Z and host health became ready 6.568 seconds into
  the diagnostic. Host /health returned 200 with the expected service/status;
  warmed round-trip samples were 6-18ms, with first-ready response about 102ms.
- Two exact configured health-command invocations succeeded in 1.522/1.876s;
  those wall times include Docker CLI/engine/Python startup, not HTTP alone.
  Minimal python-pass invocations took 0.268/0.373s. Separate instrumented probes
  measured urllib imports 0.705/0.537s and HTTP 0.051/0.032s, both returning 200.
- Docker itself reported healthy. The new native health sample at
  2026-10-18T20:01:56.546084019Z exited 0 after 1.28949s. Docker retained earlier
  failed health-log entries from the previous attempt; those older timestamps
  are not new failures. The previous timeout did not recur on this unchanged
  retry. These results do not establish a root cause or justify claiming a fix.
- The diagnostic stopped backend again and verified all three exact apps exited.
  Source data/auth/roles/catalog/schema/sequences/both histories were independently
  compared to the fresh baseline and live/rehearsed inventories after stopping;
  all match. DB identity/image/start/restart count/mounts and health are unchanged.
  No resources were created/deleted, no source writes or mail occurred, and all
  recovery hashes/evidence remain retained. Safe results:
  .tmp/task064-diagnostic/diagnostic-summary.json and diagnostic-final-summary.json.
- Independent helper review identified a potential cleanup gap if a later inspect
  failed before stop; it did not occur in this successful run. The ignored helper
  was subsequently hardened to always attempt stop on its already-pinned immutable
  backend ID. Syntax passed; this hardened failure branch was not runtime-tested
  or used for another restart. No application, Compose or dependency code changed.
- No new unit/backend suite was rerun for this operational diagnostic; the 90
  isolated checks above remain its earlier result. Backend process readiness is
  verified, not DB connectivity/authenticated UI or full-stack readiness.
  Full app activation requires recovery direction; do not replay SQL or claim
  the whole of Task 064/Ticket 69.4 complete yet.

## User-started stack and Git handoff

- The user independently restarted PostgreSQL and rebuilt/started frontend and
  backend, then authorized read-only testing and commit/push to master. The
  preceding off-state/activation-pending notes describe those earlier phases.
  This final phase performs no starts/stops/rebuilds, SQL upgrades, repairs,
  seed replays, login/OTP actions, record writes or reminder sends.
- Current PostgreSQL retains ID
  06438f44071a29fb405b6afc8569e1dcaa575b3c23163b0fcd3f75c7f658dd4e,
  pinned image and monitor-dev_postgres-data, with user restart time
  2026-10-18T20:07:27.610825244Z and restart count 0. Backend is now
  389705d73e2bf56863c46f42a468e2a7a700b4fe557c4e8305b1286aa1354087;
  frontend is 6ca53154b4d6df184d4f5b3ca97d3b388bc2d4c3a694084b565e4c2e57dafe9a.
  Mailpit retains its original ID. These user actions are not agent restarts.
- At 2026-10-18T20:13:40.442901Z, enforced read-only SQL verified two validated
  user FKs use RESTRICT, five meter-child FKs retain CASCADE, nine domain tables
  and both histories exist, roles remain one admin/one regular user, and no
  memberless/orphaned mappings or creators exist. Counts remain 2/4/4 users/
  meters/memberships, 7 balances, 4 top-ups, 16 challenges/sessions each, no
  reminders and 8/1 history rows. Source identity/health stayed stable throughout;
  no old-fingerprint repair was required or attempted after user startup.
  Safe proof: .tmp/task064-handoff/db-readonly-summary.json.
- At 2026-10-18T20:14:01.053598Z, 13 anonymous GET checks passed: health, UI/deep
  link, transformed main/App and both supplied logo assets returned 200; protected
  me/meters/members routes returned 401 through both backend and frontend proxy.
  Both logos match the supplied asset bytes. OpenAPI hash and all six installed
  dependency pins exactly match approved Task 063. No new backend-suite run or
  per-request latency measurement is claimed for this handoff.
- A preceding metadata sample failed a transient health-state assertion before
  HTTP/evidence writes; its exact affected service/state was not retained.
  Immediate follow-up and the full passing run show all four running/healthy,
  restart count 0, with identical selected metadata before/after. No intervention
  occurred; uninterrupted health or a fixed root cause is not claimed.
  Safe proof: .tmp/task064-handoff/http-summary.json; private handoff evidence
  remains beside the recovery set, excluded from Git.
- README/context now show the current running stack and completed 69.4. The
  user-approved Git handoff contains only current/work documentation; runtime
  source/config/schema/dependencies are unchanged. Local and origin master
  matched before staging. No force push, unrelated edits or private files.
- Final independent documentation/privacy review passed. Local links and
  whitespace passed across nine active/task documents; git diff --check passed.
  Protected runtime/test/schema/config/dependency/research paths have no diff.
  The handoff stages only the six current documentation files and this task's
  prompt/results, not private evidence or ignored verification helpers.
