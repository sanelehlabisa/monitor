# Repository Context

Monitor is a software-only prepaid-electricity planner: email login -> named
meters -> manual balance/top-up kWh records -> transparent estimates.
The root [README](../README.md) owns stable roadmap IDs and priority. Component
READMEs hold details; historical results stay in work/ and Git.

## Current contracts

- FastAPI uses explicit Psycopg SQL, not an ORM. React/Vite/Material UI is the
  mobile-friendly frontend. Development uses software/dev.docker-compose.yaml
  and ignored software/.env. Never print/commit secrets or private records.
- Task 083 uses direct docker compose with exactly dev/prod files and one ignored
  software/.env plus its safe example. The production browser origin is
  https://monitor.roventics.com. Following Job Talk, production joins external
  roventics_proxy as monitor-frontend and serves internal HTTP80, with a private
  127.0.0.1:8082 diagnostic binding. The backend/database have no host ports.
  Shared Roventics Nginx owns public HTTP80 redirects, HTTPS443 and certificates.
  Development overrides local URLs/ports and Mailpit SMTP in Compose; no env
  edits are needed when switching modes. Production has three services and no
  Mailpit. No launcher, profiles or custom startup script. Nginx derives the
  canonical authority with a map; backend origin validation remains required.
  The frontend health check uses internal HTTP. Public certificates are not
  mounted into Monitor. Standalone local HTTPS is superseded by the shared edge;
  development remains independent. Database
  URL/CORS remain derived; no user mode/log-level settings or backend fallbacks.
  software/nginx/README.md owns network/proxy/certificate setup instructions.
  Repository preparation does not perform live VPS/DNS/certificate changes.
- Task 078 removes settings.py and pydantic-settings entirely. Existing database,
  auth, mail, startup and scheduler modules read os.environ directly; no renamed
  configuration class/module or new loader. Preserve current env keys, secrets,
  canonical origin/HTTPS, SMTP TLS, cookie policy and aware UTC cutoff checks.
  Pydantic request/response schemas remain, explicitly pinned to the existing
  runtime's 2.13.5 version for API compatibility. The user subsequently rebuilt
  production; Task 079 confirms the running backend no longer has settings.py.
- A meter needs only a name. Task 063 backend code authorizes current members or
  DB admins, including permanent deletion of a meter/history. Last-member removal
  is rejected; leaving does not delete a meter. Task 064 applied the live FK
  transition; the user-started full stack passed read-only smoke checks then.
  Task 071 later found all four source containers already stopped and preserved
  that state; never infer permission to start them from historical checks.
- Record actual remaining kWh (non-negative) and purchased kWh (positive), with
  editable occurrence times separate from audit times. Store UTC instants;
  the browser converts local input/display.
- Open OTP signup creates a regular user after verification. Authorized sharing
  may create one first, without a session or OTP bypass. Returning login preserves
  users.type; that constrained user/admin column is the sole authority,
  read each request. No env/email override or cookie-cached role. Preserve opaque
  HTTP-only cookies, digest-only OTP/session storage and abuse controls.
- Fresh-only seeds/010-users.sql provisions hlabisasanele730@gmail.com as admin
  in both modes, without credentials/sessions. Development additionally uses
  seeds/020-demo-meters.sql for a fictional account, meters and history; production
  never seeds meters. Later role changes are manual DB
  operations, never startup or login re-promotion.
  Each mode has its own persistent volume; existing volumes never replay seeds.
  Task 079 explicitly restored the existing approved production account to admin
  at the user's request, preserving other roles and all records. Reload the browser
  after manual role changes; admins default to My and select All for global scope.
- The UI has an open white layout, blue/teal Monitor branding, compact system
  typography, stacked logo/name, Back and email/red icon-labelled Sign out.
  Task 079 removes the unnecessary software-only tagline from the login screen.
  Task 082 uses a simple 2 by 2 forecast grid (stacked below 360px), responsive
  values and subtle dividers. The footer keeps only Roventics attribution.
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

Task 080 uses a labelled fixed 10 kWh/day starting assumption with exactly one
actual balance at or before calculation time. With two or more valid readings,
use measured per-meter usage with positive elapsed time and intervening top-ups.
No balance stays Not enough data; negative consumption/inconsistent chronology
stays unavailable rather than falling back. Genuine zero use has no finite run-out.
The existing available status with intervals_used=0 identifies the starting
assumption in the UI and monthly email; legacy low-balance warnings still require
measured intervals. This is not the research simulator's calibrated prior.

The deterministic time-weighted rate produces estimated current balance and
remaining days/run-out. Task 066 uses the strictly-next UTC 1st and its full
calendar-month datetime duration: max(0, daily_usage * planning_days - CURRENT
estimated_balance). This is not total usage, Rand cost or a future-balance
projection. On the 1st advance again; rate/current-balance/run-out math stays.
The API replaces the old 30_days key with recommended_monthly_top_up_kwh and adds
planning_at (target UTC month-start, not calculation time) and planning_days.
Task 081 adds monthly_requirement_kwh = daily_usage * planning_days, without
subtracting balance. The compact UI shows Monthly requirement and Additional
top-up separately; unavailable forecasts keep both values null.
Calendar metadata is known even when kWh estimates are unavailable. Preserve
latest actual reading/time and calculation time; never adopt a research prior.

UI calendar dates remain UTC; factual ledger/run-out timestamps stay browser-local.
Recalculate after ledger changes/Refresh, at UTC rollover and on resuming an
outdated view. Local bounded timers do not poll the API. Version/busy/error guards
and one automatic attempt per expired workspace/cycle protect writes/navigation;
read failures keep manual Refresh recovery. Task 069 activates the monthly
scheduler locally with internal Mailpit; production/external mail remains separate.

## Database and runtime safety

- database/ keeps schema.sql, numbered seeds/ and README.md. PostgreSQL runs SQL
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

## Current source layout (Tasks 060-062 and 078)

060 retired old setup/stale active context. Backend logic lives under
app/modules, Pydantic validation under schemas and routers under endpoints;
main/database and version-bearing __init__ stay at app root. Task 078 removes
settings.py and reads configuration directly in the existing consumers.
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
3. Ticket 69 is complete for accepted monthly-only/local Mailpit scope. Task 068
   (published as f74b650) supplies the finite durable pass; Task 069 adds the app
   lifecycle loop, startup recovery and sequential off-event-loop 60-second passes.
   Use current members (including newly shared users), not admin access alone.
   Discover only the latest missed eligible cycle; retry all saved new-format
   pending cycles. Preserve original target-month/user keys, full fan-out before
   SMTP, independent recipient commits, the 30-minute lease and parent/claim/member
   rechecks. Unknown legacy/malformed monthly keys block automatic writes; never
   remap old send-month keys, drop pending jobs or reset sent history silently.
   MONITOR_MONTHLY_REMINDERS_ACTIVATED_AT is an optional saved aware UTC cutoff:
   blank disables; invalid/naive/numeric values reject. Do not regenerate on
   restart. Cooperative worker drain, reminder-only DB bounds and 120-second
   backend shutdown grace preserve API behavior. Sharing adds only a collapsed
   schedule note. Legacy creator-only opt-in low-balance/CLI code stays manual;
   shared/automatic low-balance alerts are explicitly deferred and not scheduled.
   All 157 backend/43 frontend checks, build and isolated real SMTP lifecycle/
   restart checks pass; API/pins are unchanged. Approved READ ONLY source audit
   found zero deliveries; pinned internal Mailpit/no relay gates passed. One
   backend recreation retained image/mounts/other env and activated cutoff
   2026-10-19T21:19:54.201423Z in ignored software/.env. Other three services retain
   IDs/start times/volumes; health 200 and frontend signed-out proxy 401 pass.
   First eligible send: 31 October 2026, 09:00 UTC (target 1 November). No source
   delivery records/forced mail, external SMTP, backup or schema work. Owned test
   resources are cleaned; details/evidence are in work/069. Production/external
   activation needs separate approval. Preserve recovery/research/history artifacts.
4. Task 070 / Ticket 57.1 production preparation for monitor.roventics.com is
   complete: own production Compose/volume, schema-only fresh setup and shared-edge
   instructions. Task 072 consolidates its example into the single .env.example.
   Its historical plan reused Job Talk's VPS Nginx/host Certbot with an internal
   HTTP80 app hop and external roventics_proxy. Task 083 restores that shared-edge
   wiring and fresh admin-only production seeds after Task 077's local correction.
   Backend retains scoped
   proxy trust and SMTP egress.
   Production monthly automation is forced off; the dev cutoff cannot carry over.
   Both production targets build with cached dependency layers. Isolated local
   HTTPS/OTP/secure cookies/meter/ledger/forecast/logout, changed-IP two-hop DNS
   recovery and DB restart/recreation checks pass. Owned resources are cleaned;
   running-app identities/volumes, .env and frozen public inputs are unchanged.
   No external mail, source SQL/service actions, public certificate or new backup.
   Local self-signed TLS/anonymous Mailpit are not real-provider/VPS acceptance.
   Ticket 57.2 retains separately approved live
   deployment/acceptance; actual VPS/DNS/certificate state is unverified. Task 069
   was subsequently published to master as 0d029ae; completion-time no-Git notes
   are historical. Preserve compact real-user phone/browser walkthrough 65.
   HTML email 70 and offline forecast validation 66 stay separate;
   a new candidate model is not required for the pilot. Then collect evidence 56/67.
   Each implementation needs its own questions, prompt and approval.
5. Task 071's initial local assessment is historical in work/071: core browser,
   sharing/admin and bounded API auth/access checks passed; it identified minimal
   deployment gaps addressed by Task 072. The stopped CSRF/framing probe was not
   retried and no exploit is claimed. Full OS/native scanning, physical/household
   validation and actual VPS/TLS/provider acceptance remain outside local proof.
6. Task 072 implements approved minimal pilot hardening in 64 config lines:
   one ignored software/.env plus one .env.example, Nginx 1.30.6, browser-origin
   write checks/anti-framing headers and public-edge OTP budgets (10/minute/IP,
   burst 5; 60/minute aggregate, burst 10; 429). Headerless clients still require
   backend auth; no new service/dependency/env policy knobs or backend changes.
   Both Compose modes, production builds, nginx -t, 16 benign policy cases,
   response headers and bounded per-client/aggregate limits pass. Real UI login,
   meter/ledger/forecast/reload and Sign out/reload401 pass at desktop/390px.
   The untracked production example has verified ignored recovery in
   .tmp/task072/retired/.env.production.example; historical helpers stay intact.
   Source env/services/data are untouched and remain stopped as found. Next is
   separately approved VPS setup with actual shared-edge patch-status inspection
   and real TLS/SMTP acceptance, not extra infrastructure or a model rewrite.
   Final cleanup and handoff proof are recorded in work/072. On 21 October 2026
   the user authorized committing/pushing completed Tasks 070-072 to master;
   earlier no-Git notes describe their implementation-completion scope. This
   publication request does not authorize VPS or source service actions.
7. Tasks 070-072 were committed/pushed to master as 52a0e1d after user approval.
   Task 073 implements the approved explicit-environment contract on 22 October
   2026: its 11 backend installation fields were required, normal validation errors
   hide input values and invalid-cutoff errors do not echo the literal. Only the
   saved reminder cutoff was optional/off. Log-level wiring was completed there,
   not added as a new verbosity feature; Task 074 removes that unused setting.
   Production mode/reminder-off remain fixed.
   At that task's completion ignored .env had APP_DOMAIN and matched 17 example keys;
   hashes confirm all 16 previous values/cutoff are preserved. No sibling secrets
   copied. Its Mailpit/development values were not converted for the VPS.
   Frontend internal 80 is explicit Compose metadata; shared public HTTPS and
   no-host-binding behavior are unchanged. All 33 focused checks, 11 missing-field
   app-startup checks, lifespan/health/CORS and both Compose modes pass in an
   isolated network-none backend container. All 12 required production inputs
   reject omission. Source services/data stay unchanged; no restart or Git/VPS
   action. Exact cleanup and verification limits are recorded in work/073.
8. Task 074's implementation/isolated verification are historical in work/074.
   It introduced validated origins/local HTTPS and removed user mode/log-level
   keys, retaining ten required backend fields. Task 075 supersedes its public
   URL/profile/development-setting instructions, not its preserved work records.
   Its retired Bash/certificate helpers have preserved recovery copies, not current
   setup instructions; generated private certs stay ignored. No standalone local
   TLS service remains in the amended scope.
   Production frontend80/backend8000 remain private, its volume initializes schema
   only when empty, and reminders stay off. Both production images build with
   cached dependencies; frontend TypeScript/Vite compilation ran afresh. All three
   Compose modes and 12 missing-input checks pass. An isolated network-none run
   passes 82 focused settings/main/CORS/auth API checks and ten missing-field app
   import/startup checks. All 20 frontend startup cases pass (three valid,
   seventeen invalid); Bash SAN/CA:false and non-overwrite checks pass, preserving
   both certificate-file hashes on rerun. The actual optional TLS edge passes certificate/SAN and
   HTTPS/API OTP checks with captured mail, Secure cookies, correct redirect
   host/port, meter create/rename, two balances/one top-up yielding 4 kWh/day and
   logout401. These are local API checks, not real-provider/browser/household proof.
   All 14 unrelated actual .env values retain their hashes, including credentials
   and the saved cutoff; all four source services stay stopped/unchanged through
   smoke checks. The obsolete backend/.env.example was retired only after Git and
   ignored-copy recovery verification. Windows NTFS key ACL protection is not
   verified; the script requests restrictive creation/chmod without changing trust.
   Exact cleanup removes five owned containers, five networks, one synthetic
   volume and two image tags; zero owned resources remain. Source stopped-service
   metadata and public runtime hashes are unchanged. No source startup, real email,
   credential rotation, Git or VPS action; full results belong in work/074.
9. Task 075's amended two-file implementation/static checks are historical in
   work/075. It fixed dev URLs/ports/Mailpit and kept production values explicit;
   no backend fallbacks were added. Production images and static missing-input
   checks passed, but isolated startup timed out before API-flow verification.
   No end-to-end success was claimed. Exact cleanup removed five containers,
   five networks, one synthetic volume and two tags; source state stayed unchanged.
   Task 076 supersedes its HTTP-only loopback/port-variable instructions, not its
   preserved records or the two-file/three-production-service boundary.
10. Task 076's implementation/isolated checks are historical in work/076. The
   production→nginx move preserved files/private certificate hashes, and the
   prior fixed8443 HTTPS/API OTP/session/meter/ledger/4 kWh/day/logout checks passed.
   Both images, synthetic same-env modes/VPS variant and missing-input checks
   passed. The helper's SAN/CA:false/non-overwrite checks passed; exact cleanup
   removed four containers, five networks, one synthetic volume and two tags,
   preserving all four stopped source containers. No new browser/provider/VPS
   acceptance was claimed. Task 077 supersedes the old local8443 URL/binding,
   not the preserved records, certificates or two-file/three-service boundary.
11. Historical Task 077 removed its launcher and custom origin script and fixed
   local frontend80/443 and backend8000. Task 083 supersedes those local bindings
   with the requested Job Talk-style shared proxy; direct Compose and development
   overrides remain. The earlier local-only setup is not current deployment guidance.
   Earlier launcher/configuration/HTTPS API checks and exact cleanup remain
   historical in work/077; do not present them as verification of later edits.
   The later user-reported startup failure was fixed by replacing only the public
   example OTP secret in ignored .env with a random 256-bit value. The failing
   production backend was recreated and its already-created frontend started;
   both are healthy. Database identity/start time/mounts remained unchanged.
   Read-only HTTP redirect/HTTPSroot200/backendhealth200/signed-out401 passed.
   SMTP then pointed to Mailpit; provider settings are installation-owned. No email,
   source SQL, VPS or Git action occurred. The subsequent user choice explicitly
   requested removal of settings.py, handled separately by Task 078.
   The preceding isolated local correction passed direct config,
   production builds, Nginx validation, HTTP80-to-HTTPS443, backend8000 health
   and isolated captured-OTP/meter/forecast/logout. Its separate evidence is in
   .tmp/task077-local; see work/077 for cleanup and preservation results.
12. Task 078 removes the settings object and dependency, updating callers to direct
   environment reads and reminder functions to a parsed activation datetime.
   Login/session, SMTP, database and reminder behavior remain the contract.
   Final images built; all 218 backend checks, identical OpenAPI and isolated
   HTTPS/captured-OTP/meter/forecast/logout passed. Owned fixtures were cleaned.
   Existing credentials and source containers were preserved during that task;
   the user subsequently rebuilt the backend. Results/recovery are in work/078.
13. Future mobile/local-only 68 may provide guest device storage and optional
   account login; it does not weaken today's authenticated backend.

## Git handoff

Git handoff: on 25 October 2026 the user authorized committing/pushing completed
Tasks 073–082 to master. Earlier no-commit notes record completion-time scope.
Feature checks pass, but shared-VPS deployment still needs the public proxy/TLS
route with OTP limits, installation credentials, explicit first-admin assignment
and live acceptance. Current Compose is local-only and forces monthly mail off.

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
