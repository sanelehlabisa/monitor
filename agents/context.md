# Repository Context

Monitor is a software-only prepaid-electricity planner: email login -> named
meters -> manual balance/top-up kWh records -> transparent estimates.
The root [README](../README.md) owns stable roadmap IDs and priority. Component
READMEs hold details; historical results stay in work/ and Git.

## Current contracts

- FastAPI uses explicit Psycopg SQL, not an ORM. React/Vite/Material UI is the
  mobile-friendly frontend. Development uses software/dev.docker-compose.yaml
  and ignored software/.env. Never print/commit secrets or private records.
- A meter needs only a name. Task 063 backend code authorizes current members or
  DB admins, including permanent deletion of a meter/history. Last-member removal
  is rejected; leaving does not delete a meter. Task 064 applied the live FK
  transition; the user-started full stack passed read-only smoke checks and remains running.
- Record actual remaining kWh (non-negative) and purchased kWh (positive), with
  editable occurrence times separate from audit times. Store UTC instants;
  the browser converts local input/display.
- Open OTP signup creates a regular user after verification. Authorized sharing
  may create one first, without a session or OTP bypass. Returning login preserves
  users.type; that constrained user/admin column is the sole authority,
  read each request. No env/email override or cookie-cached role. Preserve opaque
  HTTP-only cookies, digest-only OTP/session storage and abuse controls.
- Fresh-only seeds provision hlabisasanele730@gmail.com as admin and fictional
  examples, without credentials/sessions. Later role changes are manual DB
  operations, never startup or login re-promotion.
- The UI has an open white layout, blue/teal Monitor branding, compact system
  typography, stacked logo/name, Back and email/red icon-labelled Sign out.
  /meters lists profiles; /meters/<uuid> supports direct login/reload/history.
  / and /meters/ remain compatible entries; login is not a separate URL.
- Estimates lead; record forms/history open on demand. Search is server-side by
  name/member email, shown above 10 unfiltered meters or for an active query.
  Preserve request-version guards, form resets and unavailable/error recovery.
- Task 065 adds collapsed Sharing below History: email Add and confirmed
  Remove/Leave. My uses GET /api/meters?mine=true for current memberships,
  including shared-in admins; All retains global admin scope. Search/reloads/counts
  follow that scope. Creator fields are labelled Created by, never access rules.
  Saved sharing changes use read-only Retry; self-leave clears/navigates to the
  list immediately, with separate list-retry recovery. Ignore stale async replies.

## Forecast boundary

All callers use one run_forecast_model function with that meter's history:

    consumed = previous_balance + intervening_top_ups - current_balance
    daily_usage = consumed / elapsed_days

Require at least two actual readings with positive elapsed time. Include top-ups
and surface impossible negative consumption/inconsistent chronology. Show
Not enough data/Inconsistent history instead of inventing numbers. Genuine
zero use has no finite run-out date.

The deterministic time-weighted rate produces estimated current balance and
remaining days/run-out. Task 066 uses the strictly-next UTC 1st and its full
calendar-month datetime duration: max(0, daily_usage * planning_days - CURRENT
estimated_balance). This is not total usage, Rand cost or a future-balance
projection. On the 1st advance again; rate/current-balance/run-out math stays.
The API replaces the old 30_days key with recommended_monthly_top_up_kwh and adds
planning_at (target UTC month-start, not calculation time) and planning_days.
Calendar metadata is known even when kWh estimates are unavailable. Preserve
latest actual reading/time and calculation time; never adopt a research prior.

UI calendar dates remain UTC; factual ledger/run-out timestamps stay browser-local.
Recalculate after ledger changes/Refresh, at UTC rollover and on resuming an
outdated view. Local bounded timers do not poll the API. Version/busy/error guards
and one automatic attempt per expired workspace/cycle protect writes/navigation;
read failures keep manual Refresh recovery. No reminder scheduler is activated.

## Database and runtime safety

- database/ keeps only schema.sql, seed.sql and README.md. PostgreSQL runs SQL
  only on an empty volume. Startup never upgrades SQL or replays seeds. Agree
  an explicit safe repair for partial initialization; never reset automatically.
- Task 059 upgraded the existing DB after verified backup/isolated rehearsal,
  promoting only the approved existing admin. Preserve nine domain tables and
  BOTH monitor.schema_migrations and public.schema_migrations history tables.
- Task 060 retires inactive SQL/runner sources, not stored history. The database
  README records recoverable SQL/backups. Preserve pending work, backups,
  research archives, refocus.md and historical work records.
- At Task 060 preflight, monitor-dev-database-1 was healthy/running on
  monitor-dev_postgres-data; backend/frontend/Mailpit remained stopped as agreed.
  Recheck actual state before work. Tasks 060-062 do not authorize source starts.
- Task 064 applied exactly two FK changes after fresh recovery verification
  (zero required backfills), preserving records, roles, auth state, sequences and
  both histories. Do not replay that transaction, seeds or role assignments.
- After the initial health timeout and successful bounded diagnostic, the user
  independently restarted PostgreSQL and rebuilt/started the app services.
  Read-only UI/API/schema smoke checks passed; all four were left running.
  PostgreSQL retains the same ID/image/volume, with user restart time
  2026-10-18T20:07:27.610825244Z and restart count 0. App IDs/images changed through
  that user action, not an agent rebuild. Historical identities stay in work/064.
  One transient health-state sample was rejected before HTTP; the subsequent
  full smoke run was healthy throughout. No probe fix/root cause is claimed.
  The final handoff made no service actions, DB writes, login sessions or mail.
- Run checks against isolated labelled DB/Mailpit resources, never source data
  or real email. The finite reminder CLI can send mail even with --help; verify
  by import/isolated checks only.
- Live browser login/end-to-end verification after 059 is outstanding. Isolated
  HTTP checks are not live-user or household validation.

## Current source layout (Tasks 060-062)

060 retired old setup/stale active context. Backend logic lives under
app/modules, Pydantic validation under schemas and routers under endpoints;
main/settings/database and version-bearing __init__ stay at app root.
Frontend login/meters screens live under routes, meter-only components under
routes/meters, shared navigation under components and helpers under lib.
Keep behavior, URLs, validation and permissions unchanged; add no dependency,
framework/layer, compatibility shim or eager re-export architecture.
All 67 backend and 33 frontend checks passed; OpenAPI is byte-identical and
TypeScript/Vite plus mocked browser checks passed using pinned Docker deps.
The host node_modules has missing MUI declarations and was left unchanged.
At those tasks' completion source services remained stopped; only isolated
verification resources were used and cleaned. Details/recovery are in the work
records. The user authorized the
Git handoff of completed Tasks 059-062 to master (2f8af81); earlier no-commit notes
describe completion-time state. Task 063 was subsequently committed/pushed to
master as 59e7e20. The user approved Task 064's live-transition prompt and app
startup. Its DB and activation checks passed. The user subsequently authorized
testing the already-running stack and publishing Task 064 to master; earlier
no-commit/off-state notes describe their completion-time state.

## Shared backend (Task 063)

GET/POST /api/meters/{id}/members lists/shares by email; DELETE /{user_id} removes
membership. New accounts default user; preserve existing roles. No invitations,
global directory or auth bypass. Member/creator metadata never overrides scope.
Parent locks plus separate access rechecks serialize member changes, meter/ledger
writes and dispatch. Any member/admin may permanently delete the meter/history;
last-member removal is rejected even for admins. Fresh targets restrict creator/
member-user deletion rather than cascading shared data. There is no account-delete
API/transfer workflow. Work-record upgrade.sql was explicitly applied once in
Task 064, never by startup SQL; it must not be replayed against the current DB.
Backfill only memberless interim meters, never re-add a creator who already left
an otherwise shared meter. Legacy opt-in reminders require creator membership
and recheck before SMTP; fan-out/schedule redesign remains 69.7. UI sharing and
admin My membership presentation are implemented by Task 065; old owner fields
stay compatible. The optional mine query does not widen regular-user scope.
All 90 isolated backend checks passed, including concurrent/revoked writes.
Copy-only upgrade/restore, fresh-schema equivalence and read-only current-code
checks passed; owned verification resources were removed, evidence retained.
Existing API payloads are unchanged; only three member operations were added.

## Remaining priorities

1. Ticket 69.4 is complete through Tasks 063/064: backend checks, preserved-data
   cutover and running-stack read-only smoke passed. Task 065 implements 69.5's
   approved collapsed Sharing and membership-scoped My/All/search. It does not
   change SQL schema, forecasting, auth, reminders or source service state.
   All 92 isolated backend/36 frontend checks, production asset build and 12
   mocked-browser groups pass. Running-source metadata/static smoke also passes;
   services retain IDs/images/start times and are running/healthy. Verification
   details are in work/065. The user subsequently authorized its Git handoff to
   master on 19 October 2026 as 1e638c3; prior no-commit notes describe completion-time scope.
   Live OTP/write/browser validation remains separate from anonymous smoke.
2. Task 066 completes 69.6: exact target-month math, current balance, strictly-next
   UTC 1st and separate run-out. All 109 isolated backend/43 frontend checks,
   TypeScript/Vite build and 11 mocked-browser groups pass, with no live data or
   mail. OpenAPI changes only the agreed recommendation key and two metadata
   fields. Results are in work/066-calendar-month-planning/changes.md.
   It is not research Ticket 66 or a new learned model.
   Task 067 was approved and removes only the visible " (UTC)" monthly-date suffix;
   UTC date formatting, calculations, rollover and API remain unchanged. All 43
   frontend checks and the TypeScript/Vite build pass. The user subsequently
   authorized the Git handoff of completed Tasks 066–067 to master as 03a2e4d; earlier
   no-commit notes describe their original completion-time scope.
3. 69.7 is automatic month-end mail at 09:00 UTC to current meter members, with
   DB-backed status and backend-startup catch-up, not skip-if-offline. Split into
   69.7.1 durable member/cycle dispatch and 69.7.2 asyncio lifecycle/startup recovery.
   Task 068 completes 69.7.1's inactive finite member-based monthly pass in
   app/modules/monthly_reminders.py. Discover only the latest missed cycle and use
   current members, including newly shared users; admin access alone is not a
   subscription. Retry all saved new-format pending cycles. Require an explicit
   aware activation cutoff; exclude cycles before meter creation. Keep failed
   claims pending with the existing 30-minute lease. Commit the full fan-out before
   SMTP and each recipient independently, with parent/claim/membership rechecks.
   All 134 isolated backend checks and real Mailpit SMTP checks pass (three messages,
   two members, no duplicate send). OpenAPI is byte-identical and pins unchanged.
   Source IDs/images/start times/restarts/volumes are unchanged; all four services
   were healthy in the post-verification sample, not continuously throughout.
   No source SQL, mail or service action occurred. Details are in work/068.
   The user subsequently authorized the Git handoff of completed Task 068 to
   master; earlier no-commit notes describe its completion-time scope only.
   Current user_meters has no join timestamp. Preserve legacy rows/CLI without
   reinterpreting old send-month keys as new target-month/recipient keys. Legacy
   pending/sent reconciliation and fixed cutoff persistence gate 69.7.2 activation;
   this finite slice does not complete legacy backlog recovery.
   Source-mail activation requires explicit approval; do not hot-reload an active
   scheduler into the running stack. The existing CLI remains finite, creator-only,
   opt-in/default off and hidden in UI; the new helper is not wired into it,
   requests or app lifecycle. Low-balance behavior stays unchanged. Reuse raw SQL/claims/SMTP, not a
   new service. A later retry must not overwrite its original delivery-cycle key.
4. HTML email 70 (plain fallback/trusted app links), usability 65, offline forecast
   validation 66, deployment 57, then household/external evidence 56/67.
   Each implementation needs its own questions, prompt and approval.
5. Future mobile/local-only 68 may provide guest device storage and optional
   account login; it does not weaken today's authenticated backend.

## Deferred research

Tariffs/Rand/cost forecasts, payments, hardware, camera/OCR, MQTT, device ingestion
and ML are not V1. Preserve research and non-invasive safety rules; anomalies are
never proof of theft. Read-only Switch UI/Roventics brand inspection is allowed;
never modify sibling repositories without separate authorization.

Offline forecasting research has its own dependencies/environment under backend.
simulator.py is the sole entrypoint: 730-day synthetic replay, nominal 0.1 sec/day,
moving orange 60/90-day context, two plots and a randomness slider. The forecast
horizon remains 30 days. Its calibrated prior/rolling line is NOT integrated.
Retain 66.1/66.2 acceptance, 66.3 review, chronological 66.4 go/no-go and fresh
66.5 approval. Current independent-noise evidence favors baselines, not adoption.
Preserve ignored .tmp/task053/legacy-research.zip and
.tmp/task055/simulator_checks.py: they contain unique retired research sources.
