# Task 069: Automatic Monthly Reminders

Status: approved implementation, verification and local Mailpit-only activation complete. Ticket 69 is complete for its accepted monthly-only scope. Subsequent Git publication authorized on 20 October 2026.

## Context and reuse

- Read agent instructions/context/rules/template, relevant component READMEs and existing monthly pass, lifespan/settings, database and SMTP boundaries.
- Task 068 is committed/pushed to master as `f74b650a5a7853a5cd6eb06abe91eca7604a60c8`; its 134 backend checks and isolated SMTP verification remain the baseline.
- User confirmed monthly planning only. Shared low-balance fan-out/automatic warnings are deferred rather than silently treated as completed Ticket 69 functionality. Legacy opt-in code remains unchanged and is not scheduled.
- User excludes new backup work. Preserve existing backups/data/history/research; no schema or data upgrade is proposed.

## Approved activation boundary

- One optional aware UTC cutoff is both the enable switch and durable first-activation boundary. Persist it in ignored `.env`; Compose must pass it explicitly. Empty remains off; invalid/naive values fail closed. There is no per-user setting or startup-generated cutoff.
- Before every automatic pass, block unresolved monthly legacy/malformed keys. An aggregate read-only source inventory and internal-Mailpit-only target check precede activation. Do not reinterpret send-month keys, drop pending jobs or reset sent history.
- The approved prompt authorizes one backend-only recreation after isolated checks and a successful activation gate. Other source services/volumes stay untouched; no external SMTP, forced reminder, source test record or new backup is authorized.
- A nonempty incompatible legacy inventory or non-Mailpit SMTP target stops activation pending a separate explicit decision. Ticket 69 is not complete if an activation/reconciliation gate remains unresolved.
- A failed post-recreation health/activation check stops further actions and reports the actual backend/scheduler state, without pretending a started worker is disabled or silently recreating it again.
- Await real worker drain during shutdown; cancellation of asyncio.to_thread does not stop SMTP. Bound reminder-owned DB operations, preserve finite SMTP timeouts and match Docker grace to the documented shutdown behavior.

## Preparation checks

- Passed git diff --check, explicit whitespace checks, all 43 local documentation links and the eight-path documentation-only allowlist.
- Independent read-only prompt/active-doc review found no substantive blocker. Explicitly documented failed post-activation verification without promising a running worker is disabled or authorizing repeated recreation.
- No runtime/config edits, source DB/environment inspection, mail, service action, backup or Git publication occurred. Implementation tests have not run for this preparation.

## Implementation and reuse

- Added one lifespan-owned scheduler module and integrated the existing app factory. One optional `MONITOR_MONTHLY_REMINDERS_ACTIVATED_AT` ISO datetime enables monthly automation and persists its UTC cutoff; blank disables, invalid/naive/numeric inputs reject. No startup-generated cutoff or per-user controls.
- Startup runs immediately, then checks every 60 seconds without overlapping local passes. Blocking DB/SMTP and interruptible interval waits run off the event loop. Stop signals are checked during discovery/before SMTP; incomplete fan-out rolls back, accepted mail commits before stopping, and actual worker completion is awaited during shutdown/cancellation.
- Reused Task 068's finite pass/claims, membership checks, ledger readers, model and plain-text SMTP builder. Automatic passes block incompatible monthly keys before claim writes; existing finite/legacy CLI behavior remains unchanged. Legacy low-balance code is preserved but not scheduled.
- Reminder-owned connections have 5-second connect/statement and 2-second lock waits. Existing SMTP timeout is 10 seconds per operation, not a guaranteed total-send duration. Backend Compose has 120-second shutdown grace; forced process termination can still repeat accepted SMTP mail before its DB commit.
- Added only one body2 policy note inside collapsed Sharing and its existing assertion. No controls/handlers/layout changed. API/schema/dependencies/auth/roles/forecast math are unchanged.
- Review size is 186 changed implementation/config lines, under the approved 250-line exception. Runtime read-only review found no remaining blocker.

## Isolated verification

- All 157 backend checks pass in 27.21 seconds (134 existing plus 23 new scheduler cases), exit 0. Tests cover blank/invalid/UTC-persisted settings, no-worker/no-DB disabled mode, responsive health during work, sequential safe retries, normal/cancelled worker drain, legacy pending/sent blocking, connection bounds and cooperative discovery/send stops.
- Canonical OpenAPI is byte-identical to Git HEAD f74b650; SHA-256 `a4b6ffa7fca1688fda9a31e3bb0ec9a9d7df6d3ecf8a327fefddb27d15e0b171`. All six backend requirement pins match cached images; no install/fresh build is claimed.
- Real internal Mailpit SMTP and actual app lifespans recovered three pending jobs for two example.test members. Admin-only access received none; restart sent zero duplicates, disabled startup started no pass, maximum concurrent passes was one, and both workers drained. Existing sent history was retained (four final sent rows including one pre-sent fixture). The exact isolated smoke DB was dropped.
- Lifecycle health responses took 0.0384/0.0317 seconds and shutdown drains 0.0035/0.0026 seconds in that synthetic check; these are not source/VPS performance guarantees.
- All 43 frontend checks passed (10.17 seconds), plus TypeScript/Vite build (931 modules, 1.52 seconds) with all 12 pinned versions matched. Existing >500 kB chunk warning remains; no dependency or bundling scope was added.
- Three exact-owned backend-test containers, one synthetic PostgreSQL volume and one internal network were removed at 21:15:59 UTC, plus the separate network-none frontend build container. Source identities/images/start times/restarts/volumes and public input hashes matched again at 21:16:09 UTC; source services were healthy at those samples. No source actions occurred during verification.
- Evidence: ignored `.tmp/task069/summary-069-9f9328ee71c2.json`, `post-cleanup-source.json` and `build-result.json`; private logs/contracts/hashes retained outside Git/OneDrive at `%LOCALAPPDATA%/Monitor/verification/task069-backend/20261019T211441Z-069-9f9328ee71c2/`.

## Live activation

- Approved bounded REPEATABLE READ READ ONLY inventory found zero source delivery rows: no legacy pending/sent keys to reconcile, no dropped/remapped records. Pinned internal Mailpit:1025, development mode, no auth/relay/forward config/mounts and the shared Docker alias were verified. Intended Compose/env matched the current stack except the reviewed cutoff/grace changes.
- Saved the first-activation cutoff `2026-10-19T21:19:54.201423Z` once in ignored `software/.env`, preserving all other backend environment values. Next eligible send is 31 October 2026 at 09:00 UTC, for the 1 November planning cycle; no pre-feature cycle is discovered.
- Exactly one approved backend recreation was attempted at 21:21:56 UTC and verified at 21:22:07 UTC. Old ID `389705d73e2bf56863c46f42a468e2a7a700b4fe557c4e8305b1286aa1354087`; new ID `9205468e62982a6a8727df659a0bfd0485f7caa39c0f23c8ebb69ce4d62d7f19`. Image, mounts and all other backend environment values match; 120-second stop grace and saved cutoff match runtime.
- PostgreSQL, frontend and Mailpit retain their IDs/images/start times/restart counts/volumes. Backend is running/healthy; /health returns 200 and signed-out /api/me through the unchanged frontend proxy returns 401. App startup completed with no fixed scheduler-failure/compatibility warning markers.
- Post-activation aggregate remains zero delivery rows. No source test records, forced reminder, external SMTP, source schema/ledger/auth/member writes or backups occurred. Only the backend container was replaced; its previous ephemeral container state is not retained, while image/source/data/evidence remain.
- Activation proof: ignored `.tmp/task069/activation-preflight.json` and `activation-result.json`, with a one-attempt-only activation helper. Independent read-only code/evidence review found no blocker. Completion does not claim live-user OTP/write validation or production/external email delivery.
- Independent post-activation metadata/health/hash review passed at 21:23:59 UTC, 118.8 seconds after backend start. Fixed cutoff, image/mount, 120-second grace and other service identities remain correct; all four services were healthy at both samples, /health 200 and no scheduler warning markers. Verified runtime/config/test hashes still match isolated checks. No additional SQL/mail/service actions were used; proof is ignored `.tmp/task069/post-activation-source.json`.

## Final handoff

- Final git diff --check, explicit whitespace checks, the 18-public-path allowlist and all 43 relative documentation links pass. The ignored local `.env` contains exactly one activation key matching the verified runtime cutoff; no secrets/private evidence are staged or published.
- Accepted Ticket 69/69.7/69.7.2 are marked complete; shared low-balance automation stays deferred. Next valuable work is the real-user walkthrough (65), then minimal deployment (57), not a model rewrite or backup project.
- No commit/push was performed at implementation completion. On 20 October 2026 the user subsequently requested committing and pushing Task 069 to master, before preparing the production Docker/HTTPS ticket. This supersedes the completion-time Git exclusion, not the runtime/deployment boundaries.
