# Monitor software

Active V1 path: manual balance/top-up kWh entry -> FastAPI -> PostgreSQL ->
deterministic forecast -> Material UI dashboard. Hardware and OCR are not active
dependencies.

The owner reports the current deployed release working on 1 November 2026. Task
089 plans guest web onboarding next; it does not change runtime behavior.

## Components

- [Backend](backend/README.md): authentication, meter ledger APIs and forecasting.
- [Forecast research](backend/research/forecasting/README.md): isolated synthetic
  datasets, plots and a rolling-linear simulator, not an application dependency.
- [Database](database/README.md): PostgreSQL, Psycopg, fresh SQL bootstrap and
  separately approved additive upgrades.
- [Frontend](frontend/README.md): mobile-first manual entry, estimates and history.
- [OCR](ocr/README.md): preserved future research only.

## One environment, two Compose files

Keep only ignored `software/.env` and the safe `.env.example`; do not create
per-mode environment files. Use `APP_BASE_URL=https://monitor.roventics.com` for
the production browser origin behind the shared Roventics Nginx/Certbot proxy.
There are no profiles or user mode/log-level settings.

| Mode | Compose files | Browser URL |
| --- | --- | --- |
| Development | `dev.docker-compose.yaml` | `http://localhost:5173` |
| Production | `prod.docker-compose.yaml` | `https://monitor.roventics.com` |

Development fixes frontend/API/database ports at 5173/8000/5432 and always uses
internal Mailpit. It ignores production URL/SMTP settings, so no `.env` edits are
needed to switch back to development. Database credentials, OTP secret and the
saved local reminder cutoff remain explicit. Production always forces reminders
off and requires real SMTP plus a unique OTP secret. From `software/`, run either
Compose file directly:

```sh
docker compose -f dev.docker-compose.yaml up --build
docker compose -f prod.docker-compose.yaml up --build
```

Production has three services and no Mailpit. Its frontend serves internal HTTP80
and joins the external `roventics_proxy` network as `monitor-frontend`, matching
the existing shared-proxy contract. The existing Roventics Nginx handles public
HTTP80 redirects, HTTPS443 and certificates. Monitor publishes only a private
frontend diagnostic port at `127.0.0.1:8082`; backend and database ports remain
unpublished. No launcher, profile, binding variable or extra Compose file is needed.
Set up the shared network, proxy route and certificate coverage using the
[production operator guide](nginx/README.md) before public use. Production now
requires that shared edge; standalone local HTTPS is no longer its setup.
Development remains independent and keeps its captured-mail overrides.
Task 077's earlier isolated local HTTPS checks remain historical in its work
record; they do not establish real-provider or VPS acceptance.

## Development stack

Copy [.env.example](.env.example) to `.env` only if it does not exist, then choose
the installation's database password. Keep one ignored `.env` per installation;
both Compose modes use it, and the same example documents the required values.
Never overwrite an existing environment or reuse the local secrets for production. Administrator
authority comes only from `users.type`, not environment settings. Task 059's
guarded source transition passed after backup/rehearsal and approval to stop
writers. Task 064 separately applied the shared-backend FK transition after a
fresh backup/restore/rehearsal and exact live preservation checks. Do not rerun
that transaction or fresh seeds. Following the initial health timeout and bounded
diagnostic, the user independently restarted/rebuilt the full stack. Read-only
UI/API/schema checks passed; all four services were left running then. Task 071
later found all four already stopped/exited and preserved that state. No health-probe
configuration change was made. Fresh initialization is not an existing-volume
upgrade. For an approved fresh setup:

```powershell
docker compose --env-file .env -f dev.docker-compose.yaml up --build
```

The frontend is at `http://localhost:5173`, the API health endpoint at
`http://localhost:8000/health`, Mailpit's captured-email UI is at
`http://localhost:8025`, and PostgreSQL is available on localhost port 5432.
Host bindings remain loopback-only. Mailpit's SMTP port 1025 is available only
inside the Compose network.

Stop the stack without deleting data:

```powershell
docker compose --env-file .env -f dev.docker-compose.yaml down
```

On an empty development volume, PostgreSQL runs `database/schema.sql`,
`database/seeds/010-users.sql` and `database/seeds/020-demo-meters.sql` in order.
The user seed creates the approved admin; the development seed creates fictional
meters/history under a separate demo account. Production mounts only the schema
and user seed, so all production meters are created manually. Restart/recreation does not replay
SQL, duplicate examples or overwrite roles. The API no longer executes or mounts
numbered migrations. Existing data is preserved but not automatically upgraded;
never use volume deletion or fresh seeds as an upgrade/partial-init repair.
The [database README](database/README.md) documents recovery and the retained
reviewed upgrade copy. Task 059 safely upgraded the current DB after a fresh
backup/rehearsal; do not rerun that one-time transition or fresh seeds.

Backend and frontend sources are bind-mounted for reload; Uvicorn watches only
`app/`, not the offline research environment. Rebuild after changing
Python or npm dependencies. The ignored `.env` is the visible source of Compose
development values; Compose reports required missing values instead of silently
using backend fallbacks. The single committed `.env.example` documents production
settings; Compose fixes local ports and development overrides URL/mail values.
The current production guide covers the shared Roventics proxy and certificate setup.
Task 078 removes `settings.py` and `pydantic-settings`; the existing backend
modules read the same ten required runtime values directly from `os.environ`.
Validation remains beside each consumer without another configuration layer or
private values in error messages. Compose maps the one `.env` and derives its database
URL and fixes the backend mode. Development supplies local CORS/SMTP values;
production derives its runtime CORS/gateway origins from `APP_BASE_URL`.
Do not duplicate runtime URL/mode keys
in `.env` or add another loader.
Blank local SMTP credentials remain valid when explicitly supplied. The reminder
cutoff alone remains optional; see [backend settings](backend/README.md#runtime-settings).

Current features are email OTP/cookie login, name-only meter management,
member/admin access, on-demand email sharing, membership-based My/All views,
server-side search and timestamped balance/purchase history.
The open blue/teal Material UI workspace uses linkable `/meters/<uuid>` details,
on-demand record forms and a prominent forecast summary with manual Refresh.
One deterministic model derives estimates from each meter's own history and
withholds unsupported forecasts. Task 066 plans the strictly-next UTC 1st using
the full target month's actual days and current balance, with read-only rollover
refresh. Reminder controls stay hidden. Task 069's optional saved activation
cutoff enables monthly member emails through the app lifecycle; local activation
uses internal Mailpit only. The legacy opt-in creator-only CLI remains available
but is not scheduled. Component READMEs show
the source layout, API contracts and repeatable demo. Historical UI iterations
remain in their numbered work records rather than current setup instructions.

After changing frontend dependencies, refresh an existing named volume:

```powershell
docker compose --env-file .env -f dev.docker-compose.yaml run --rm --no-deps frontend npm ci
docker compose --env-file .env -f dev.docker-compose.yaml restart frontend
```

The existing frontend dependency volume survives image rebuilds. Refresh it
after lockfile changes, then restart Vite so it loads the new dependencies.
Frontend file watching uses polling for reliable Docker Desktop bind-mount
reload. A practical local walkthrough is in the frontend README.

## Production images (Task 036 preparation)

The Dockerfiles now have named `development` and `production` targets.
Development Compose explicitly selects `development`; reload, ports and runtime
environment values remain. Task 058 replaces migration startup/mounts with
fresh PostgreSQL initialization. Build the production images
from `software/`:

```powershell
docker build --target production -t monitor-backend:production ./backend
docker build --target production -t monitor-frontend:production ./frontend
```

Production is also the default Dockerfile target. The frontend serves built React
assets through internal Nginx HTTP80 behind the shared public HTTPS edge.
The frontend health check uses internal HTTP; public certificates stay at the
Roventics edge. No separate Monitor proxy service or launcher is added.
The backend runs Uvicorn privately on port8000, with no host publication,
without reload, as a non-root user. No local `.env*` files enter either build.
Runtime credentials must not be passed as build arguments or copied into images.

To run, the frontend needs a reachable `backend:8000` name on its Docker network.
The production image explicitly sets production mode; backend environment reads
do not fill missing installation values. Supply all ten runtime values,
including a unique `MONITOR_OTP_HMAC_SECRET`, through the deployment configuration.
Schema installation and upgrades are not performed by the image command. See the
component READMEs for the runtime boundaries.

Task 070 added [prod.docker-compose.yaml](prod.docker-compose.yaml) and a shared
HTTPS design under Ticket 57.1. Task 083 restores the existing shared proxy
wiring after the historical local-only iterations. The [operator guide](nginx/README.md)
covers the required external `roventics_proxy` network, Monitor route and shared
certificate coverage. Task 072 consolidated the template into one
[.env.example](.env.example). Production uses a separate database volume and
initializes only the schema and `010-users.sql`, never demo meters/history.
Automatic production monthly reminders stay off pending separate activation.
The two-file configuration and direct Compose commands are retained.
`APP_BASE_URL` is the only public URL setting. The production file has three
services, with no Mailpit, added TLS edge, profile or override. Credentials, SMTP
values and saved reminder cutoff stay intact.
Task 078 removed the settings object; the user subsequently rebuilt the backend.
Keep the generated OTP secret and supply provider SMTP before production email login.
Production Compose fixes production mode and monthly reminders off as safety
policy; it never inherits the local cutoff.
Live deployment remains unapproved;
no VPS, DNS, public certificate or household database changes are included.
Both production targets build in Task 070 using cached dependency layers. Local
self-signed HTTPS/OTP/cookie/meter/ledger/forecast checks, changed-IP proxy recovery
and database restart/recreation persistence pass. All task-owned resources are
cleaned; source services, environment and frozen public inputs stayed unchanged.
Real provider SMTP, public certificates and VPS state remain unverified. See
[Task 070 results](../agents/work/070-production-compose-https/changes.md).
Both production and development images built successfully in Task 036 after Docker
recovered. Disposable smoke checks passed for static assets, SPA fallback,
proxied API errors/cookie headers, process health and production-secret refusal.
Only task containers/network were removed; existing development services and
stored data were untouched by these checks.

## V1 product boundary

Users manage nickname-only meter/property profiles and manually enter actual
balance and top-up energy in kWh. V1 does not require a physical meter number,
tariff, Rand amount, device credential, image or OCR result. Task 080 shows a
labelled 10 kWh/day starting estimate from one actual balance; two or more valid
readings supply the meter's measured rate. No balance remains "Not enough data",
and inconsistent history stays unavailable. Distinguish actual records from estimates.

Actual production deployment, payment integration, MQTT, hardware and OCR remain
out of scope until their roadmap status changes through an approved task.

## Planned validation and release

Tasks 042, 050 and 056 record requirements only; they implement none of these
tickets. Refocus 69 is complete for monthly-only/local Mailpit use. Next are a
compact real-user usability check 65 and minimal deployment 57; HTML presentation
70 and offline forecast research 66 are separate, not a mandatory model rewrite.
Personal 56/external 67 testing follows deployment.
The root README owns IDs and cross-product priority. Ticket 66's candidate
research does not automatically replace the app.

### Ticket 69: Database and Access Refocus

- 69.1 recovery verification passed in Task 057; Task 058 accepts the additive
  target without authorizing changes to the existing database.
- 69.2 adds schema.sql/seed.sql for fresh persistent Docker volumes and an
  explicit upgrade script. Task 058 passed fresh/copy-upgrade, persistence, both
  reload paths and source-preservation/cleanup checks. Its 64 backend checks
  used cached image dependencies; a network-disabled fresh build could
  not fetch uncached pip requirements, so no fresh image build is claimed.
  Rehearsal uses only a restored copy. Existing-volume execution needs approval,
  never a reset or seed hidden in startup. Both reload paths are retained.
- 69.3 / Task 059 uses DB user/admin types as the sole role authority and removes
  active admin environment configuration. The guarded source transition and
  68 isolated backend checks passed; resource cleanup is verified.
  Signup stays open and defaults to `user`; every request reads the
  stored role through existing OTP/session user queries. Fresh setup seeds the
  approved admin; the guarded existing-volume transition promotes that existing
  account only once, stops if absent, and leaves every other account `user`.
  Later role changes are manual DB edits, never overwritten by login or restart.
- 69.4 adds shared membership and authorization across every protected meter,
  ledger, dashboard and reminder endpoint, with full global admin access and
  safe concurrent last-member protection. Task 065 implements 69.5's collapsed
  sharing controls and server-scoped My/All/search, not a UI redesign. Remove/Leave
  changes membership only; Retry after a saved change never repeats the write.
- 69.6 / Task 066 supersedes the former fixed-30-day plan: use the strictly
  next UTC 1st, its full calendar-month duration and current-balance subtraction.
  Keep usage learning/run-out unchanged; do not project balance to that future date.
- 69.7 sends automatic monthly mail at 09:00 UTC on the last calendar day to meter
  members, not all application users; admin access alone does not subscribe anyone.
  69.7.1 covers persisted per-recipient/cycle dispatch and retryable status;
  69.7.2 adds an asyncio lifecycle loop and backend-startup catch-up using the DB.
  Task 068 completes the inactive finite pass: discover only the latest missed
  cycle, use current members (including newly shared users), and retry saved
  new-format pending work. All 134 isolated backend checks and real Mailpit SMTP
  checks pass; OpenAPI/pins are unchanged. Persist a fixed initial cutoff and
  reconcile legacy delivery keys
  before separately approved source-mail activation in 69.7.2. No user selectors,
  new service or dependency. The user confirmed monthly-only automation: shared
  low-balance delivery stays deferred; the legacy opt-in path is not scheduled.
  Task 069 completes the lifecycle loop and saved optional UTC activation cutoff;
  all 157 backend/43 frontend checks, build and isolated SMTP lifecycle checks pass.
  An empty legacy audit and internal-Mailpit checks preceded one backend-only
  recreation. Other services/volumes remain unchanged; no backup/schema work.
  MONITOR_MONTHLY_REMINDERS_ACTIVATED_AT is blank/off in examples. Set it once to
  an explicit aware UTC instant to enable an installation; retain that cutoff on
  restarts. Invalid/naive/numeric values reject. Current local cutoff is saved in
  ignored `.env`; the first eligible send is 31 October 2026 at 09:00 UTC, into
  Mailpit. Production/external SMTP activation remains Ticket 57 work.

Keep the existing eight domain tables plus membership (nine total), including
separate reminder settings/delivery claims, hashed OTP/session state and real
occurrence times. Rates stay derived from each meter's history. Exact safe
transition, deletion/onboarding and scheduling policies must be settled in the
relevant implementation prompt. Database details are in the
[database README](database/README.md); role/access/reminder details in the
[backend README](backend/README.md); sharing/planning controls in the
[frontend README](frontend/README.md). Task 058 changes bootstrap and app-only
development reload, leaving the current DB untouched then. Task 059 moves
authority to DB roles while retaining owner access and the same public API/cookie
contract; sharing is not enabled. See backend/database guidance for manual role
changes and the verified guarded source transition. No source login/session
writes or real emails were needed for those checks. Task 064 subsequently applied
the preserved-data FK transition; its initial health gate failed, but the later
user-started full stack passed read-only checks and remains running. See its work
record for the historical stopped-state diagnostics; no SQL replay is needed.

### Ticket 70: Readable HTML Emails (planned)

After 69.7's recipient/message contract, reuse the SMTP boundary for readable
HTML OTP and reminder messages, with plain-text fallback, escaped names and
trusted links to the existing app routes. Links retain ordinary login and meter
access checks; no new authentication channel, notification service or magic token.
Implementation detail/acceptance is in the backend README.

### Ticket 68: Guest web onboarding

Promote browser guest use now; retain native/PWA installation as later 68.5.
The current deployed release still requires email login. The proposed first guest
release starts with one local meter and the existing kWh balance/top-up entry
pattern. Do not require a meter serial number, email or personal details to try it.

**68.1 - Small storage contract (first).** Reuse meter/ledger shapes behind a
small set of storage functions: local browser data when logged out, existing
API when signed in. Keep components/calculations reusable; no storage framework
or duplicate app. Review current API/SQL only to identify real coupling; a
browser store needs domain fields, not replicas of auth/reminder tables.
No new indexes/tables or schema rewrite for storage selection. Record any
demonstrated blocker before proposing a separate data-preserving DB change.
Confirmed: Log in and save uploads the existing guest meter/history after verified
email login, in that same flow without a separate transfer screen. Settle the small
retry/reconciliation rule in the design; done when this contract is approved.

**68.2 - Browser forecast parity (after 68.1).** Implement the existing deterministic
formula in one small frontend module for private local guest inputs. Use shared
example inputs/reference outputs from Python; don't replace the live backend
model or add ML. Match default/measured/unavailable states, rounding and UTC month
rules before connecting UI. Detailed cases live in the frontend README.

**68.3 - Guest workspace and records (after 68.2).** Reuse forecast and ledger
components for balance/top-up add/edit/delete, immediate recalculation and browser
storage according to 68.1. Show clear persistence/unavailable states and a local
clear action. Done when first result, reload, storage failure and data-change
flows work without sending guest ledger information to the server.

**68.4 - Login and storage routing (after 68.3).** Homepage offers Use without
logging in alongside email login. A guest-only Log in and save to account prompt
leads through existing OTP and disappears when signed in. Guest operations use
local storage; authenticated operations use the backend through the same small
meter/ledger boundary. Do not add a separate Copy to account step.
The user confirmed that this explicit action saves existing local meter/history
after successful OTP. Keep local originals and report online success only after
the server confirms the writes. Cover duplicate/retry/partial success in that
same flow, saving into a new account meter without overwriting existing/shared
meters. Ordinary login does not import guest data implicitly. No automatic two-way
synchronization or repeated import on every login.
Failed authenticated writes must not silently fall back to a local store;
preserve the draft and show recovery. Logout must not copy account data into
the guest store. Verify login/expiry/logout, storage choice and member/admin access.

**68.6 - Keep me signed in (after 68.4).** Add one unchecked-by-default option
to email login. Current runtime always issues a 30-day persistent session;
replace that policy only in this approved implementation slice. Confirmed checked
lifetime: 3 days. Unchecked: browser-session cookie with
a short server-enforced absolute lifetime (proposed 24 hours; settle in the prompt).
Use the existing opaque random token/digest table and cookie flow; no new auth
table, refresh-token service or browser-stored credential. Persistent-cookie and server
expiration must agree; no silent indefinite extension. Preserve secure HTTP-only,
SameSite, host/path scope, origin/CSRF checks, OTP limits and logout revocation.
Existing sessions keep their recorded expiry unless separately approved.
Verify remembered return, expiry/revocation, unchecked behavior, rejected origins
and guest usability after an expired session; reuse existing checks/manual flows.
Browser session restoration is not guaranteed logout; server expiry is authoritative.
Backend/frontend detail lives in their READMEs.

**68.5 - Later installation/mobile.** Revisit PWA/native packaging, offline app
loading, synchronization and notifications only after pilot evidence. Browser-local
data does not imply that first load or offline reopening already works.

After 68.4 and 68.6: Ticket 65 reviews guest and existing account usability, 57.3 deploys,
then 67.1 recruits and 67.2 observes. Existing users/data/authentication are preserved.

### Ticket 66: Offline Per-Meter Forecast Research

Task 050 splits the existing validation parent into 66.1 example datasets,
66.2 consumption transformation/plots, 66.3 a candidate versus the current
baseline, 66.4 chronological backtests/go-no-go and 66.5 separately approved
integration. Each depends on the previous stage; 66.5 needs a positive decision
and fresh approval. Task 051 starts 66.1/66.2 with small generation/plotting scripts
under `backend/research/forecasting/`. Matplotlib stays in a research-only virtual
environment; outputs are ignored and excluded from backend Docker build context.
Both subtickets remain open for remaining acceptance work. Task 052 replaces the
earlier segmented-candidate plan with one rolling 90-day (optionally 60-day)
ordinary least-squares consumption line. Task 053 makes simulator.py the sole
normal entrypoint: one nominal 10 kWh/day household, two graphs,
three planning estimates and a Low/Mid/High randomness slider. The slider varies
daily use and purchase-timing jitter, not average usage or missed-record probability.
It restarts the same-seed run and clears its scores without retraining the frozen
prior. Scenario/speed/manual-entry controls and the error sidebar are removed;
detailed comparisons stay in headless JSON/CSV exports. Old utility scripts are
retired only after exact-byte archival; outputs/environment/history are preserved.
Task 053's 20 focused checks, headless exports and native GUI verification passed.
These stationary random examples do not establish improved forecasting or prior
accuracy. NumPy and Matplotlib remain research-only.
Task 055 defaults to 730 days at a nominal 0.1-second timer interval (plus
rendering overhead) and shades the moving 60/90-day context orange on both
graphs. This replays two years; forecasts still cover 30 days, not two years.
The check script is removed at the user's request after local backup. Headless
and native GUI smoke checks passed; earlier test results remain historical.
Full candidate review, validation/go-no-go and integration approval remain open.
Run instructions and current limits are in the research README.

The live model already calculates from each meter's own history. Research uses
synthetic files only, with dense usage truth separated from daily/weekly/irregular
manual observations. No real/demo DB changes, pooled customer histories or
physical device processing. The simulator's calibrated defaults remain labelled
experiments; Task 080 separately adopts a fixed 10 kWh/day live starting assumption
with one balance, not its trained prior or regression. The simulator's
starting rate is the median of separate fictional training households' observed
ledger rates, frozen independently of demo duration, randomness, lookback and
reset. Fixed 10 kWh/day remains a labelled initial/fallback and comparison, not
evidence of a real household's usage. No forecast is shown without a balance.

Preserve the current weighted average as a baseline. Sparse records cannot prove
hourly patterns; labelled interpolation is not an actual reading. Compare future
consumption or a declared no-future-purchase balance/run-out scenario, not a
forecast supplied with future records. Keep monthly usage distinct from extra
kWh to buy. Detailed outputs and acceptance checks are in the backend README.
If the candidate is not justified, retain the validated baseline; adoption is not
required for deployment. No subtask is authorised merely by this planning record.

### Ticket 56: Personal Usage Validation

Retain Task 034's completed technical checks. Use real household kWh readings,
top-ups and observation times; keep synthetic demo/screenshot histories separate.
Save each forecast snapshot/time and compare it with later actual readings,
accounting for intervening top-ups. Record balance/run-out error, confusing
inputs, missing information, recommendation usefulness and repeat-entry behaviour.
Acceptance is a dated evidence summary and prioritised findings, not a claim of
validated accuracy without real comparisons. Can begin with 67 after 57.

### Ticket 57: Web Deployment

Current status: the owner reports the existing deployment working (1 November
2026); 57.2 records that report. The older preparation evidence below remains
historical, not a claim that deployment is still waiting to begin. No new VPS
inspection or security certification is claimed by Task 089.

**57.3 - Deploy the guest iteration (after 68.1–68.4, 68.6 and 65).** Reuse existing Compose,
domains, Nginx/certificates and environment. Review the exact release before
operator deployment; preserve users, meter history, roles and other sites. Verify
fresh browser guest entry/result/local reload with no guest-ledger network upload
before the explicit authenticated save, successful history saving/retry after OTP,
email login/logout, current admin/shared-meter permissions and protected deep links.
Record release/version and a simple application rollback path that preserves
records; no new backup service or database reset. Done when the deployed iteration
passes these focused flows; don't infer this from a local build alone.


Task 071's [local browser/security-readiness results](../agents/work/071-browser-security-readiness/changes.md)
record four passed real desktop/mobile functional groups and passing bounded
API auth/access checks using synthetic accounts/captured mail. NOT READY for
security-cleared merge/deployment at that assessment: it found an affected Nginx
1.30.5 pin and missing aggregate OTP-abuse controls. Origin evidence was incomplete, with no
demonstrated CSRF fixture mutation; framing/UI sign-out were not reached (API
logout passed). Full OS/native and real VPS/provider checks remain open.
Only owned test resources were removed; source data/services/.env stay unchanged,
with all four source services stopped as found. Task 071 made no fixes or Git/VPS actions.
Task 072's [minimal hardening results](../agents/work/072-minimal-pilot-hardening/changes.md)
patch the gateway, add browser-origin/framing policy and public-edge OTP budgets,
and use one environment example. Both Compose modes/builds, gateway policy/headers,
bounded rate limits and the real desktop/phone-width meter flow including Sign out
pass locally. The candidate can proceed to review and separately approved live
57.2 setup/HTTPS/SMTP acceptance. Inspect the actual shared edge's patch status;
no whole-image security certification or public-provider acceptance is implied.

Task 083 prepares `monitor.roventics.com` using the existing shared Nginx/Certbot
route: Monitor serves private HTTP80 and joins `roventics_proxy`; the shared
edge supplies public HTTPS. The active guide covers certificate coverage without
dropping existing names. No VPS, DNS, certificate issuance or live data changes
are executed by this repository preparation; preserve the existing sites.

- 57.1 / Task 070 (complete, isolated checks passed): production Compose, explicit minimal env/origin/secrets,
  private backend/database, persistent fresh-schema setup, shared proxy
  integration and certificate issuance/renewal instructions. See the
  [operator guide](nginx/README.md); no VPS verification is claimed. Task 083 adds
  the approved admin seed to fresh production setup and keeps demo data dev-only.
- 57.2: initial release deployed by the owner and reported working. Preserve
  that installation; its historical checklist is not a new instruction to
  reconfigure DNS, certificates or data. Verify changed flows under 57.3.
- Production monthly automation requires a separate explicit fixed activation
  cutoff; never copy the local Mailpit cutoff. No public Mailpit/database/debug
  endpoints, startup seed replay/role promotion or automatic existing-volume upgrades.
- Keep actionable secret-free logs and simple privacy/contact/removal guidance.
  Retain the real-user walkthrough (65); adopting research model 66.5 is not a
  deployment prerequisite. No new backup work in this PoC scope; preserve existing
  recovery artifacts. Live deployment/external mail need separate approval.

### Ticket 67: Monitor beta recruitment and one-month observation

**67.1 - Final Reddit post/repost (after 57.3 and 65).** Prepare a short post and
small screenshot/demo explaining kWh inputs, estimates, guest-local versus account
storage, limitations and one feedback/contact route. Check current rules in the
chosen community, identify the creator honestly and invite about 3-5 volunteers.
Review before posting; creating this ticket does not send messages or publish.
Done when the agreed post is published and the small cohort/feedback route is ready.

**67.2 - Observe roughly 30 days (from cohort start).** At entry, note voluntarily
reported first-estimate success/time and confusing steps. Offer a short weekly
check-in on repeat entries, estimate usefulness, storage loss and problems. At
about day 30, summarise findings and choose a small next change, continue or stop.
Collect consented, non-identifying notes; never collect guest history for analytics or
silently add analytics/session replay. There is no default ability to track local
users' return visits; report observation gaps honestly. Aggregate existing account
usage only within an agreed privacy scope, without raw records/emails in Git.
Done when the dated summary covers participation, repeat use (where volunteered),
usefulness, issues and prioritised fixes. Recruitment is not evidence of demand.

Personal validation 56 runs alongside, comparing volunteered real observations
with saved predictions and intervening top-ups. Keep synthetic examples separate.
Forecast research 66 and two-way sync do not gate the beta. The confirmed local-to-
account save flow must pass 68.4 before deployment.

Usability/identity/PWA detail is in the frontend README; deterministic validation
detail is in the backend README. Purchase costs and cost estimates remain
deferred because the active schema accepts kWh only.
