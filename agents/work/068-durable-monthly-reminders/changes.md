# Task 068: Durable Monthly Reminders

Status: approved implementation, verification and cleanup complete. No source delivery activation or Git publication.

The user subsequently authorized committing and pushing these completed changes
to master. Earlier no-publication statements describe completion-time scope;
this Git handoff does not authorize scheduler activation or live mail.

## Context and reuse

- Read agent instructions/context/rules/template, component READMEs and existing reminder delivery/runner code.
- Reuse raw SQL, current membership checks/locks, delivery claims, forecast boundary and SMTP abstraction; no schema/dependency change is proposed.
- Confirmed latest-only missing-cycle discovery, retries for saved pending work and all current members, including newly shared users.
- Published Tasks 066/067 are at master/origin/master `03a2e4d2cdce9790de82a513c363832ff52f3c22`; this preparation is not committed.

## Deliberate boundaries

- Task 068 implements a separately callable monthly pass, not an active scheduler. Current CLI/low-balance behavior and legacy rows remain unchanged.
- Legacy send-month keys cannot safely be treated as new target-month/recipient keys. Reconciliation of existing pending/sent jobs and fixed cutoff persistence remain explicit 69.7.2 activation gates; no legacy-backlog completion is claimed here.
- Existing 30-minute lease delays retry eligibility. Failed new jobs remain pending; latest-only limits discovery, never saved-job recovery. Removed recipients must not receive mail.
- SMTP and PostgreSQL cannot commit atomically: a crash after SMTP acceptance but before sent-status commit can repeat a message.
- During preparation no runtime/schema/test/config edits, source SQL, private record reads, mail, service actions or Git publication occurred.

## Preparation checks

- Passed git diff --check and explicit trailing-whitespace checks on all seven changed/new documentation files.
- All 38 relative documentation links resolve; changed/untracked path checks confirm documentation-only scope.
- Independent prompt review found no substantive scope or transaction-safety issue; corrected an adjacent stale database roadmap reference to 30-day quantities.
- Implementation tests did not run during preparation; no runtime code changed then.

## Implementation

- Added one 185-line finite module, `software/backend/app/modules/monthly_reminders.py`, below the approved 250-line exception. No existing runtime file was changed or activation wired.
- Discover the latest due month-end cycle after an explicit aware cutoff, excluding meters created after that due time. Commit the entire current-member fan-out before any SMTP attempt.
- Reuse existing raw-SQL claims and 30-minute lease with target-month/recipient keys. Independently commit each recipient, retain failed pending jobs, and recover old saved cycles without changing their keys.
- Own a fresh autocommit connection. Meter-before-delivery locks, exact returned claim IDs/timestamps and lease/membership rechecks protect against overlapping workers and revocation. Caller transactions are never committed.
- Reuse ledger readers, `run_forecast_model` and the monthly message builder/SMTP sender. Delayed messages separate their original cycle from fresh planning dates; unavailable history requests a reading instead of inventing numbers.
- Normalize new-path meter-name line breaks for email headers and isolate expected message/forecast date-range failures per recipient. Legacy message/forecast behavior is unchanged.
- Added 25 focused isolated cases in `software/backend/tests/test_monthly_reminders.py`. Independent read-only implementation review found no remaining blocking issue.

## Verification

- All 134 backend checks pass in 142.14 seconds (109 existing plus 25 new), exit 0, against a fresh task-owned PostgreSQL/Mailpit/backend environment. Cached image dependencies match all six requirement pins; no network install or fresh build is claimed.
- Calendar checks cover UTC/offset equivalence, exact 09:00 eligibility, leap/month/year boundaries, inclusive activation cutoff, latest-only discovery, meter-creation cutoff and future/malformed keys.
- Independent DB observers prove full cross-meter/member fan-out before SMTP and each successful recipient committed before the next send. Failed jobs remain pending until lease expiry; older saved cycles recover without resending successes. Owned-connection checks preserve unrelated caller transactions.
- Real PostgreSQL lock/lease checks cover overlapping workers, ownership loss, membership removal/deletion after selection and revocation waiting for an active send. Legacy monthly/low-balance rows and sent history are preserved; existing legacy regression checks pass.
- Actual internal SMTP to disposable Mailpit captured three messages for two example.test members, excluded the admin-only account and recorded three sent rows. A repeated pass sent zero messages. Original delayed cycle 2027-03 stays distinct from fresh planning date 2027-04-01; one unavailable-history message requests a reading. Its exact temporary fixture database was dropped.
- Canonical OpenAPI is byte-identical to Git HEAD 03a2e4d, SHA-256 `a4b6ffa7fca1688fda9a31e3bb0ec9a9d7df6d3ecf8a327fefddb27d15e0b171`. Public application/test/setup inputs were hash-stable throughout verification.
- Source container IDs/images/start times/restart counts/volumes are unchanged. All four services were running/healthy in the post-verification sample. An earlier backend unhealthy sample was recorded; uninterrupted health or a diagnosis/fix is not claimed. No source environment, private records, SQL, mail or service actions were used.
- Final git diff --check, explicit trailing-whitespace checks, nine-file allowlist, all 38 local documentation links and the 185/250 implementation-line cap pass. No API/schema/config/dependency/legacy runtime edits occurred.
- Exact-owned three containers, one synthetic PostgreSQL volume and one internal network were removed at 18:40:42 UTC after identity/label/mount checks; their ownership labels are absent. Only disposable synthetic records/mail were removed; source data and cached images remain untouched. Logs/evidence remain recoverable at the retained paths below.
- Post-cleanup source identity/runtime and public-input hash checks passed at 18:41:09 UTC; proof is ignored `.tmp/task068/post-cleanup-source.json`.
- Evidence: ignored `.tmp/task068/summary-068-cde806e64e9c.json` and reusable verification helpers; private logs/contracts/hashes are retained outside Git/OneDrive at `%LOCALAPPDATA%/Monitor/backups/task068-backend/20261019T183529Z-068-cde806e64e9c/`.

## Remaining gates

- 69.7.2 owns the asyncio lifecycle/startup loop, fixed cutoff persistence and explicit source activation after legacy pending/sent reconciliation. No scheduler/import/request/CLI wiring or real recipient mail is enabled here.
- Future limitation: extreme valid low-rate/high-balance histories may still overflow run-out datetime in the unchanged dashboard/legacy model path. The new pass retains such a failed job pending and continues; this is not a forecast-math fix.
