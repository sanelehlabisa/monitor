# Task 066: Calendar-Month Planning

## Status

The user approved with "i approve 066". Implementation and isolated/mocked
verification are complete. The user subsequently authorized committing/pushing
completed Tasks 066–067 to master; earlier no-commit notes describe their original
completion-time scope. Task 065 was committed/pushed as 1e638c3 before preparation.

## Clarifications and scope

- The user replaced the proposed unchanged-30-day policy with actual calendar
  periods, current balance only, a strictly-next-1st date, and datetime-based days.
  The prompt makes the full-target-month interpretation and numerical example
  explicit for approval; no new future-balance prediction is proposed.
- The user chose 09:00 UTC month-end mail to each meter's members, persisted sent/
  pending status and catch-up on backend startup, with no user settings. This
  supersedes the earlier saved-timezone/skip-if-offline proposal, not current code.
- Keep stable roadmap IDs: 69.6 is this forecast/API/UI slice; 69.7.1 covers durable
  per-recipient dispatch and 69.7.2 the asyncio lifecycle/startup recovery and safe
  activation. Each later implementation requires its own prompt/approval.

## Inspection and reuse

- Read agent instructions/context/rules/template and relevant frontend/backend/
  software/database README sections. Inspected the sole forecast boundary, its
  two callers, response adapter/schema, UI/date helpers, runner, delivery claims,
  settings, app lifecycle and Compose reload configuration. Independent read-only
  reviews agree this can reuse the current rate/run-out logic without a new model.
- The existing 30_days field is explicit in model/API/UI/email; rename it coherently
  rather than silently serving a different horizon under that name. UTC calendar
  display must not shift the target to the previous day on western browsers.
- The current reminder runner is finite, synchronous and opted-in creator-only;
  starting it unchanged would not deliver the new policy. Existing pending/sent
  claims are meter-level; per-recipient status, failures and cycle keys need work.
- Later scheduler should reuse the finite pass through an asyncio lifecycle task,
  keep blocking DB/SMTP work off the event loop and own/drain its worker safely.
  A request background task alone is not a periodic scheduler. No scheduler is
  started during this preparation, import, build or verification.
- Future reminder prompt must settle backlog/initial activation cutoff and late
  members (user_meters has no joined_at), preserve sent history, and distinguish
  original delivery cycle from the dashboard's strictly-next planning date on a
  delayed send. Do not silently send a historical backlog or reset delivery keys.

## Preparation checks

Only planning documents were changed during preparation. No application code,
DB/query/SQL, fixture, auth, dependency, research, service, email or sibling action
occurred then. No implementation tests were claimed. Planning whitespace/link checks
passed for the five current README/context files and both work records. A scoped
Git check confirms application/tests/schema/config have no diff. Independent
read-only prompt review found no blocker, validated the 120 kWh example and the
150-line allowance, and clarified target UTC start versus calculation time.
Existing live data, services, backups and archives stay untouched.

## Implementation and verification

- The single forecast boundary derives planning_at/planning_days from the next
  UTC month start to the following one, then uses current balance in the approved
  formula. Metadata is returned even without enough/consistent history. Learning,
  current-balance/run-out expressions, validation and rounding remain unchanged.
- Replaced the old 30_days key with recommended_monthly_top_up_kwh consistently
  in dataclass/schema/TypeScript/API fixtures and monthly message wording. No alias,
  duplicate formula, persisted forecast, future-balance model or SQL change.
- UI shows Next monthly top-up in UTC, separate from locally displayed Predicted
  run-out and existing factual/estimated labels. Actual target-day count replaces
  the old fixed-30-day note, including insufficient/inconsistent/zero-use metadata.
- The dashboard's local clock timer/focus/visibility checks use guarded read-only
  refreshes. One automatic attempt per expired workspace/cycle prevents looping
  on a stale server response; ledger errors retain the manual recovery path.
- Backend: all 109 checks passed in 26.66s (92 existing plus 17 calendar/contract
  cases). Covers 28/29/30/31 days, December rollover, exact first-day/microsecond/
  UTC-equivalent boundaries, current-balance subtraction, unavailable/inconsistent/
  zero states, unchanged run-out/rate and dashboard/email-builder agreement.
- OpenAPI comparison: only the approved recommendation rename and two required
  metadata fields changed. All other routes/properties remain identical. SHA256:
  a4b6ffa7fca1688fda9a31e3bb0ec9a9d7df6d3ecf8a327fefddb27d15e0b171.
  All six installed backend dependency pins match; requirements are unchanged.
- Backend verification used fresh task-owned DB/Mailpit resources. Exact three
  containers, one fresh volume and one internal network were removed/verified
  absent at 2026-10-19 16:09:22 UTC. Images/evidence remain; no source queries or
  service actions. Proof: .tmp/task066-backend/comparison.json and
  summary-066-117c4ab8507c.json.
- Frontend: all 43 checks (four files), TypeScript and Vite production build pass.
  The 12 installed dependency versions match package/lock pins. The existing
  >500 kB bundle warning remains; no dependency or host node_modules changes.
  The exact-owned network-none build container was removed after label/read-only
  mount checks. Evidence: .tmp/task066/build-result.json and build-5eccd799-0ea/.
- Read-only source OpenAPI/static-module checks confirm the running backend
  serves the new required metadata/renamed field without the old field, and Vite
  serves the hot-reloaded calendar panel/rollover wiring. No session, customer
  record, SMTP or mutation was used. Source containers were running/healthy with
  unchanged IDs/images/start times and restart count zero at preflight and handoff.
- Whitespace/current-doc relative-link checks pass. No SQL/schema/config,
  app lifecycle/settings, reminder dispatch/claims, research, dependency, theme,
  auth/access, AGENTS.md or refocus.md diff. Runtime changes are 91 lines, within
  both the 100-line aim and approved 150-line cap (tests/docs excluded).
- All 11 mocked-browser groups pass, with 122 synthetic API calls and four layout
  captures at 1200/390/320px (including unavailable estimates). They cover western
  timezone UTC date versus local actual/run-out, all month lengths/leap/year/1st
  rules, calendar rollover, capped local clock checks with no API polling, resume,
  duplicate suppression, unchanged expired-server metadata without retry loops,
  busy ledger/read deferral, saved-write/failed-read GET-only recovery and late
  success/error responses across navigation/account/deleted-meter cases.
  Browser errors, unexpected requests and real API requests are zero. Root
  inspected calendar-narrow-320.png: no overflow/clipping; estimates stay primary.
  One initial harness selector-quoting issue was corrected before the full passing
  replay; no runtime fix or failure was hidden. These are mocked technical checks,
  not live OTP or household accuracy validation.
- The owned Edge process exited and loopback preview closed; build container
  cleanup was verified. Evidence: .tmp/task066/results.json, browser-cleanup.json
  and calendar-*.png. Ignored evidence/profile/build files remain; no broad delete.
- Independent final runtime reviews found no blocker. Current docs/context and
  stable roadmap 69.6 are updated; next is separately approved 69.7.1 durable
  member reminders, then 69.7.2 lifecycle/catch-up/activation. No source login,
  SMTP run, live fixture write, restart/rebuild or Git handoff occurred.
