# Superseded guidance snapshot
Historical recovery copy. Use current guides for new work.

## Original `README.md`

````markdown
# Monitor

A free, software-only electricity planning application for prepaid households.
Users manually record meter balances and top-ups in kWh; Monitor uses simple,
transparent mathematics to estimate how much electricity to add and when.

## Next iteration: guest onboarding (planning only)

The owner confirmed on 1 November 2026 that the deployed app works. Preserve that
release and its users. The next change should let someone get an estimate before
email login. The owner confirmed local browser saving without an account.
No guest functionality is implemented by this roadmap update.

Guests must be able to keep balances and history in this browser without login.
Ticket 68.1 still needs confirmation on whether explicit local-to-account transfer
belongs in the first release. Login must never silently upload records.
The detailed architecture recommendation and small acceptance gates live in the
[frontend roadmap](software/frontend/README.md#ticket-68-guest-web-onboarding).

Across products, work in this order: Switch enclosure and physical testing;
Monitor guest onboarding, deployment and a roughly one-month beta; then the new
sibling `meter` research repository. These are planned tasks, not approval to
change runtime code, perform physical work, deploy or post publicly.

## V1 scope

Deliver a mobile-friendly web application that works without extra hardware,
meter integration or payment-provider access. A user signs in by email, creates
one or more meter/property profiles using simple nicknames such as Home or Shop,
and performs two primary actions:

- **Record balance:** remaining kWh and the observation date/time, defaulting to now.
- **Record top-up:** added kWh and the purchase date/time, defaulting to now.

The municipal meter number is not required. A top-up record documents energy
already purchased; Monitor does not sell electricity or execute payments.
Tariffs, Rand amounts and cost forecasts are outside V1.

Task 056 planned the database/access refocus under Ticket 69. Task 063 adds
member-based backend code. Task 064 safely applied its live DB transition after
fresh backup/rehearsal, preserving all data. The user subsequently started the
full stack; read-only UI/API/schema checks passed and all four services were left
running. The earlier health timeout did not require a code/configuration change.
Task 065 adds collapsed email sharing and membership-based My/All/search.
Task 066 adds actual calendar-month planning. Tasks 068/069 complete durable
monthly member delivery and the app-owned scheduler, activated locally with
Mailpit only. Production/external email activation remains deployment work.
Task 059 changes administrator authority to stored `users.type`,
without email/environment overrides. Its guarded source transition and 68 isolated
backend checks passed; task-resource cleanup is verified.
Task 057 verified recovery of all current data. Task 058 adds fresh-volume SQL
bootstrap and an additive upgrade script rehearsed only on a copy. Fresh/copy-
upgrade, persistence, both reload paths, source-preservation/cleanup and 64 backend
checks passed using cached dependencies; no fresh image build is claimed.
Task 058 left the existing database untouched. Task 059 then upgraded it only
after a new verified backup/rehearsal and writer-stop approval, preserving all
original records and assigning only the approved existing admin. No seed replay
or account creation occurred. Task 064's initial startup/diagnostic history is
retained in its work record. Tasks 071/072 later found all four source services
already stopped and preserved that state.

## User value

The dashboard should clearly distinguish actual entries from estimates and show:

- latest actual balance and its observation time;
- estimated current balance and daily use in kWh;
- estimated remaining days and predicted run-out date;
- next monthly top-up date (UTC 1st) and energy for that actual calendar month; and
- simple balance and top-up history.

With one actual balance, show starting estimates using a clearly labelled
10 kWh/day assumption. Valid additional readings replace it with that meter's
measured usage. Without a balance, show **Not enough data**. Manual entry must
take only a few seconds; whether users return often enough is the main V1 risk.

## Forecasting boundary

Between two actual balance readings:

```text
consumption_kwh = previous_balance_kwh
                  + top_ups_kwh_during_period
                  - current_balance_kwh

daily_usage_kwh = consumption_kwh / elapsed_days
```

Forecast work must account for top-ups between readings, preserve the difference
between actual and estimated balances, and reject zero/negative time intervals,
negative consumption and inconsistent chronology. At least two valid actual
balance readings are required before deriving a measured consumption rate.
Task 080 supplies the fixed 10 kWh/day fallback only for a single balance at or
before calculation time; existing elapsed-time and later top-up calculations
produce the estimates. Edits/deletions recalculate through the same model.

V1 uses deterministic calculations, not machine learning. Formula selection,
averaging windows, a conservative buffer and correction behavior belong in the
approved forecasting ticket and must be covered by examples and tests.

Monthly planning uses the strictly-next UTC 1st, advancing again once that day
starts. Additional kWh is max(0, rate * target_month_days - current estimated
balance), using the full target month's datetime duration, not a fixed 30 days
or a future-balance projection. Earlier predicted run-out remains separate.
The dashboard also shows total Monthly requirement (rate * target_month_days),
without subtracting balance, alongside the Additional top-up amount.

## Technology

- API/data: FastAPI, PostgreSQL and explicit SQL through Psycopg; no ORM.
- Identity: passwordless email OTP with secure HTTP-only cookie sessions.
- Web: React, Vite and Material UI with a mobile-first layout.
- Development: Docker Compose under `software/dev.docker-compose.yaml`.
- Reminders: app-owned monthly planning email to meter members when configured;
  legacy opt-in low-balance code is retained but not automatically scheduled.

The active data path is manual entry -> REST API -> PostgreSQL -> calculation ->
dashboard. No new service or AI dependency is needed.

## Deferred automation and integrations

Hardware, camera capture, OCR, device ingestion, MQTT and ML remain preserved as
future research. They should return only if real V1 usage shows that manual entry
is too inconvenient. Automated top-up/payment integrations, tariffs, Rand
forecasts, SMS, push notifications, municipal dashboards and postpaid billing are
also deferred.

Any future meter work must remain non-invasive: never open, electrically modify,
bypass or interfere with an installed meter. Anomaly output, if ever revisited,
is an investigation signal and never proof of theft or tampering.

## Repository structure

```text
monitor/
|-- AGENTS.md
|-- agents/             # rules, context, template and numbered work
|-- .github/            # PR template
|-- hardware/           # deferred camera/device research
`-- software/
    |-- backend/        # FastAPI and domain services
    |-- frontend/       # React and Material UI
    |-- database/       # active schema, fresh seeds and recovery guidance
    `-- ocr/            # deferred OCR research
```

Documentation stays in these READMEs; no `docs/` directory. Development Compose,
Docker build files and `.env.example` live under `software/`; real `.env` files
are ignored.
Use one installation `.env` with exactly development and production Compose files.
`APP_BASE_URL=https://monitor.roventics.com` is the production browser origin;
development fixes its own localhost/Mailpit settings. Compose selects the mode without profiles.
From `software/`, run `docker compose -f prod.docker-compose.yaml up --build`.
Production joins the existing `roventics_proxy` network as `monitor-frontend`.
The shared Roventics Nginx handles public HTTP/HTTPS, just as it does for Job Talk;
Monitor serves internal HTTP80, with a private `127.0.0.1:8082` diagnostic binding.
The production backend/database have no host ports. Fresh production initializes
the schema and approved admin only; development also seeds fictional meters.
See [mode settings](software/README.md#one-environment-two-compose-files) and the
[Nginx deployment guide](software/nginx/README.md).

Offline [forecasting research](software/backend/research/forecasting/README.md)
lives under `software/backend/research/`, excluded from application Docker builds.
It generates synthetic files, graph images and an offline linear replay experiment,
not live meter records or an automatically adopted application model.

## Roadmap

Ticket IDs remain stable. The order below is the current execution order, so
retained authentication IDs appear before newer product tickets.

### Completed foundation and pivots

- [x] Ticket 1: Repository Bootstrap — structure, workflow and roadmap (Task 001).
- [x] Ticket 2: Development Docker Stack — PostgreSQL, backend and frontend.
- [x] Ticket 3: Backend Baseline — FastAPI settings, health endpoint and tests (Task 003).
- [x] Ticket 4: Database Baseline — raw SQL connectivity and migrations (Task 004).
- [x] Ticket 5: Authentication Baseline — historical Keycloak work, superseded by Ticket 42 (Task 005).
- [x] Ticket 6: Frontend Baseline — historical Keycloak shell, superseded by Ticket 42 (Task 006).
- [x] Ticket 42: Remove Keycloak — clean email-OTP foundation (Task 007).
- [x] Ticket 47: Software-Only Product Refocus — manual kWh V1 context and modular roadmap (Task 008).

### Active V1 delivery

- [x] Ticket 48: Active V1 Cleanup — aligned the runtime shell and confirmed obsolete automation assumptions are absent (Task 009).
- [x] Ticket 43: OTP Storage & Policy — open signup, HMAC-only challenges and enforced limits (Task 010).
- [x] Ticket 44: Email Delivery — SMTP abstraction and isolated Mailpit development capture (Task 011).
- [x] Ticket 45: Cookie Sessions & Human Auth API — digest-only sessions and the
  request/verify/logout/me cookie API (Tasks 012-013).
- [x] Ticket 46: Email Login UI — session-aware Material UI email/OTP flow
  with Roventics branding (Task 014).
- [x] Ticket 49: User & Meter Profiles — raw-SQL nickname-only meters,
  authorised CRUD, server search and Material UI user/admin management
  (Tasks 015-018, 031-032).
- [x] Ticket 50: Balance Entries — raw-SQL storage, authorised API and Material UI entry/history management (Tasks 019, 021-022).
- [x] Ticket 51: Top-Up Entries — raw-SQL storage, authorised API and Material UI entry/history management (Tasks 020-022).
- [x] Ticket 52: Forecasting Domain — one replaceable deterministic model boundary for tested usage and planning estimates (Tasks 023-024).
- [x] Ticket 53: Dashboard & History API — authorised factual history and freshly derived forecast responses (Task 025).
- [x] Ticket 54: Forecast Dashboard UI — mobile-first estimates, honest
  unavailable states, refresh after ledger changes and a demo-focused planning
  summary with tabbed records (Tasks 026 and 033).
- [x] Ticket 55: Email Reminders — opt-in monthly and predicted-low-balance
  settings, API and finite delivery runner (Tasks 027-030). Task 033 later hid
  configuration from the PoC UI while preserving the backend and existing opt-ins.
- [x] Ticket 59: Forecast Refresh & Recovery — on-demand dashboard refresh and
  honest retry states after failed reads, without duplicate saves (Task 035).
- [x] Ticket 60: Simple Planning Dashboard — match the user's compact example:
  predictions first, two record buttons and on-demand forms/history/settings.
  Task 037 keeps forecast math unchanged and verifies desktop/mobile entry/recovery.
- [x] Ticket 61: Navigation & Linkable Meter Demo — right-aligned account menu,
  navigation Back action, meter-ID URLs and a spacious details/planning layout.
  Task 038 verifies desktop/mobile navigation and retains two synthetic meters
  owned by a separate demo user, accessible through the admin All meters view.
- [x] Ticket 62: Minimal Navigation & Typography — remove nav branding/Admin
  badge, shorten Back, enlarge the account icon and standardise text/header
  alignment. Task 039 verifies desktop/mobile styles; backend/data are unchanged.
- [x] Ticket 63: Inline Meter Management — 42px account icon, editable Name/Owner
  details and pencil/trash actions on each meter-list row, replacing bottom
  settings. Task 040 verifies owner/admin actions and desktop/mobile layouts.
- [x] Ticket 64: Compact Meter Workspace — black rounded section headers,
  white active My/All tabs, pencil-to-Save editing, first-row creation and inline
  search/clear controls. Task 041 verifies compact styles and `/meters` navigation.
- [x] Ticket 58: Monitor App Identity — supplied Monitor logo/favicon,
  blue/teal MUI theme and modest linked Roventics footer (Task 043).

### Next: usable, validated website

Tasks 042, 050 and 056 update planning only. Each ticket/subticket still needs its
own implementation approval; details live in the closest software README.

- [x] Ticket 71: Retire Legacy Setup & Context (Task 060) — keep only active SQL
  setup, verify recoverable retired sources and shorten current guidance.
- [x] Ticket 72: Backend Package Layout (Task 061) — modules, schemas and endpoints;
  preserve API/behavior and verify isolated checks after 71.
- [x] Ticket 73: Frontend Route Layout (Task 062) — route-local screens/components
  and shared helpers; preserve UI/behavior after 71.
- [x] Ticket 69: Database & Access Refocus — preserve existing functionality and
  data; reuse raw SQL, OTP, cookie sessions and the reminder runner.
  - [x] Ticket 69.1: Data Safety & Schema Review — verified full-data recovery
    (Task 057) and accepted additive nine-domain-table target (Task 058).
  - [x] Ticket 69.2: Fresh SQL Bootstrap — schema.sql/seed.sql, persistent Docker
    initialization and copy-only additive-upgrade rehearsal (Task 058).
    Task 059 separately authorizes its guarded existing-volume transition.
  - [x] Ticket 69.3: DB-Only User/Admin Roles — verified guarded source upgrade,
    open signup, stored roles and no admin-env/email fallback (Task 059).
    The one-time existing-admin assignment is not runtime email privilege.
  - [x] Ticket 69.4: Shared-Meter Backend Access — membership, full admin scope,
    all endpoint checks and concurrent last-member protection.
    Tasks 063/064 implement and verify the backend and preserved-data DB cutover.
    The user-started stack passed read-only UI/API/schema smoke checks then;
    Task 071 later found all source services stopped and left them stopped.
  - [x] Ticket 69.5: Minimal Sharing UI — collapsed member management and
    server-scoped My/All/search, retaining existing record-management flows (Task 065).
  - [x] Ticket 69.6: Calendar-Month Planning — strictly next UTC 1st, actual target
    month duration and current-balance subtraction; separate predicted run-out.
    Task 066 implements this slice; usage-rate learning remains unchanged.
  - [x] Ticket 69.7: Automatic Shared-Member Reminders — 09:00 UTC on month-end,
    durable per-recipient status and startup catch-up, without user settings.
    The user confirmed monthly planning only; shared low-balance automation is
    deferred, with legacy opt-in code preserved but not scheduled.
    - [x] 69.7.1: Durable dispatch — Task 068 implements the finite member/cycle
      pass, latest-missed discovery and saved pending recovery. All 134 isolated
      backend checks and real Mailpit SMTP checks pass. Task 068 did not activate
      the scheduler; Task 069 subsequently passed the local activation gates.
    - [x] 69.7.2: Async backend scheduler — lifecycle-owned sequential passes,
      startup recovery, safe shutdown/concurrency and explicitly approved activation.
      Persist a fixed activation cutoff and reconcile legacy delivery keys/backlog first.
      Task 069 passed 157 backend/43 frontend checks, build and isolated real SMTP
      lifecycle checks. Empty legacy inventory and internal-Mailpit gates passed;
      one backend recreation activated local automation. Other services/data stay.
- [ ] Ticket 70: Readable HTML Emails — OTP/reminder HTML with plain-text fallback
  and safe app links; reuse SMTP after 69.7's recipient/message contract.
  Task 088 completes the compact login-code presentation; reminder HTML/app links
  remain open.
- [ ] Ticket 65: Monitor Usability Review — first-user onboarding, clear actual
  readings/estimates, compact mobile states and wording; branding links to 58.
  [Task 071](agents/work/071-browser-security-readiness/changes.md) records the
  initial assessment; [Task 072](agents/work/072-minimal-pilot-hardening/changes.md)
  addresses its minimal configuration gaps and passes ordinary browser/phone-width
  flows, including actual sign-out. Household validation remains open.
- [ ] Ticket 66: Forecasting Algorithm Validation — offline per-meter research;
  retain the current calculation as the baseline, not a shared user model.
  - [ ] Ticket 66.1: Example Datasets — reproducible distinct-meter usage and
    daily/weekly/irregular manual records; hidden truth stays separate.
  - [ ] Ticket 66.2: Consumption & Plots — top-up-adjusted consumption, factual
    observations and labelled assumptions (after 66.1).
  - [ ] Ticket 66.3: Rolling Linear Simulator — one 60/90-day least-squares line,
    simple randomness replay, labelled defaults and offline comparisons (after 66.2).
  - [ ] Ticket 66.4: Backtests & Decision — chronological unseen-data comparisons,
    correctness checks and an evidence-based go/no-go (after 66.3).
  - [ ] Ticket 66.5: Approved Integration — only after a positive 66.4 decision
    and fresh approval; retain the baseline if the candidate is not justified.
- [ ] Ticket 57: Web Deployment — reuse Task 036's production images on existing
  Roventics infrastructure; no new backup work in the current PoC scope.
  - [x] 57.1: Production Compose/shared HTTPS preparation — Task 070 builds and
    isolated HTTPS/OTP/meter/persistence/DNS-recovery checks pass; temporary
    resources cleaned. Task 072 adds one shared env template and minimal tested
    gateway/OTP protections. See the [operator guide](software/nginx/README.md).
    Task 073 requires explicit installation settings, fills the missing local
    domain key without replacing values and makes internal port 80 explicit.
    Historical Task 074 implementation and isolated checks are preserved: `APP_URL` replaced
    hostname-only settings,
    removes user mode/log-level keys and adds opt-in localhost HTTPS. The VPS
    retains its shared Nginx/Certbot; production requires real SMTP and a unique
    OTP secret. All three configurations and the local HTTPS/OTP/meter/forecast/
    logout flow pass with captured mail. Test-resource cleanup is verified complete;
    no source startup or live-provider/VPS acceptance is claimed.
    Historical Task 075 verified the two-file configuration and fixed development
    URLs/ports/Mailpit. Its API flow timed out before verification, so no end-to-end
    success is claimed. Task 076 supersedes its diagnostic HTTP/port-variable setup.
    Historical Task 076's HTTPS/API/certificate checks and cleanup passed; Task
    077 supersedes its local8443 URL/binding contract, not those records.
    Historical Task 077's correction focused on local use: direct Compose, fixed HTTP80/
    HTTPS443 and backend8000 bindings, one `.env`, no launcher or external network
    prerequisite. Production has three services and no Mailpit. Earlier isolated
    HTTPS/API and cleanup results remain historical in its work record. Real SMTP
    and a unique OTP secret remain user-supplied. Task 083 supersedes that local
    wiring with Job Talk's shared-proxy pattern; the historical checks stay intact.
    Task 078 removes `settings.py` and its configuration dependency, using direct
    environment reads in existing modules. Environment values and runtime behavior
    stay unchanged; the user subsequently rebuilt the backend.
    Task 083 prepares shared `roventics_proxy` routing, internal frontend HTTP80
    and separate fresh user/demo seeds. Both modes seed the approved admin;
    production never seeds meters. Existing volumes are not reseeded or upgraded.
  - [x] 57.2: Existing authenticated release deployed — owner reports it working
    on 1 November 2026. This records the owner's deployment, not a new agent
    security audit or independently repeated VPS checks.
  - [ ] 57.3: Deploy guest onboarding after 68.1–68.4/65 acceptance — use existing
    infrastructure; verify guest/account flows and preserve users/history/sites.
- [ ] Ticket 56: Personal Usage Validation — retain Task 034's completed technical
  checks; compare real household predictions with later readings and return usage.
- [ ] Ticket 67: Small Monitor Beta — reuse the deployed 3-5-user pilot.
  - [ ] 67.1: Final Reddit post/repost and recruitment — after 57.3, prepare an
    honest short demo/post, check community rules and invite a few volunteers.
  - [ ] 67.2: Observe approximately 30 days — weekly optional feedback, repeat
    use/usefulness and final prioritised findings; no guest-history tracking by default.
- [ ] Ticket 68: Guest Web Onboarding — move browser-local use ahead of beta.
  - [ ] 68.1: Confirm guest persistence/account-handoff contract and small design.
  - [ ] 68.2: Browser forecast matching the existing calculation and UTC rules.
  - [ ] 68.3: Simple guest workspace, local records and honest storage recovery.
  - [ ] 68.4: Optional email-account entry with clear separation; explicit transfer
    only if selected, with safe retry handling and no implicit uploads.
  - [ ] 68.5: Later mobile/installable experience — evidence-led, not a guest-web gate.

### Shared execution priority

1. Switch 84.1-84.2: measure and enclose the current breadboard prototype. Use
   optional veroboard 84.3 only if it helps; no wait for the manufactured PCB.
2. Switch 55/56/57: normal operation, fix observed faults and retained internal
   reliability evidence; then 83/61/59 beta readiness and final Reddit ticket 62.
3. Monitor 68.1 -> 68.2 -> 68.3 -> 68.4 -> 65: remove the first-use account wall,
   preserve account workflows, and review the small guest experience on phones.
4. Monitor 57.3 -> 67.1 -> 67.2: deploy the accepted iteration, recruit a small
   Reddit beta and observe about one month. Personal validation 56 runs alongside.
5. Meter: establish the research problem/evidence log, then current detection,
   candidate signals and a bounded proof-of-concept decision. No full meter build.
6. Switch 85 follows PCB arrival and its bring-up gates. Monitor research 66,
   reminder HTML 70 and mobile/installable work 68.5 stay later unless evidence
   changes their priority; none blocks this guest onboarding release.

Detailed dependencies/acceptance live in the [software](software/README.md) and
[frontend](software/frontend/README.md) roadmaps. Stable IDs and historical work
records remain. This pass creates tasks only; no database reset, service restart,
deployment, Reddit posting or implementation is authorised by an unchecked ticket.

SPII and supplier timelines remain parallel and must not block independent work.
Switch details remain in [its own roadmap](https://github.com/sanelehlabisa/switch).

Tasks 051/052 established the offline datasets and rolling-linear experiment;
their results remain historical work records. Task 053 consolidates the current
workflow into one simulator: a nominal 10 kWh/day household, two graphs, three
planning estimates and a Low/Mid/High randomness slider. Levels change daily
usage variability and purchase-timing jitter, not average-usage classes or missed
records. Task 055 defaults to a 730-day synthetic replay at a nominal 0.1-second
timer interval/day, with moving orange 60/90-day context in both graphs. This is
two years of replay, not a reliable two-year forecast; the horizon stays 30 days.
The research check script was removed at the user's request after local backup;
headless/native GUI smoke checks passed. The frozen separate training prior,
60/90-day fit and offline baseline/error exports remain; no app model changes.
Task 053's 20 focused checks, headless exports and native GUI verification passed.
The current seed-42 independent-noise examples favour the baselines, not app
adoption. The full 66.1/66.2 acceptance, 66.3 review,
66.4 validation/decision and 66.5 gate stay open.

Within forecast work, finish the remaining data/validation evidence, not a live
model rewrite. The current model already uses each meter's own history. The
simulator's calibrated rates remain research experiments; Task 080's live
10 kWh/day starting assumption is separate, not a trained model. A no-go
retains the baseline; candidate adoption is not a deployment requirement if the
baseline passes validation. Detailed outputs/checks are in the backend README.

### Superseded or deferred ticket history

- Ticket 7: device ownership model — superseded by user-owned meter profiles in Ticket 49.
- Ticket 8: camera-oriented reading model — superseded by balance and top-up entries in Tickets 50-51.
- Ticket 9: earlier reading API — superseded by Ticket 53.
- Ticket 10: device authentication — deferred with automated meter ingestion.
- Tickets 11-16: camera, capture, OCR, parsing and device upload — deferred automation research.
- Tickets 17-20: earlier balance/history/trend/warning UI — superseded by Tickets 52-55.
- Ticket 21: device status — deferred with hardware.
- Tickets 22-27: placement, mount, lighting, enclosure and hardware validation — deferred.
- Ticket 28: earlier consumption estimate — superseded by Ticket 52.
- Tickets 29-32: usage-baseline, anomaly and ML research — deferred until justified by real data.
- Tickets 33-36: hardware-led self-use and beta validation — deferred; software V1 validation is Ticket 56.
- Tickets 37-39: MQTT and supported meter-interface research — deferred.
- Tickets 40-41: automated top-up research/prototype — deferred pending authorised providers and proven demand.

## Design references

Future frontend work may use `../switch/hardware/web/` as read-only inspiration
for compact mobile interactions. Company artwork may be selected from
`../roventics/frontend/images/` or `../switch/assets/branding/roventics/` in an
approved UI ticket. Monitor must implement its UI natively in React/Material UI
and must not modify either sibling repository without explicit authorization.
Task 083's requested Monitor proxy configuration is a narrow exception for
Roventics deployment files, not permission to change its site or Job Talk.

## Documentation

- [Agent workflow](AGENTS.md), [context](agents/context.md), [engineering rules](agents/rules.md).
- [Hardware](hardware/README.md), [software](software/README.md), [OCR](software/ocr/README.md).
- [Task 007](agents/work/007-authentication-architecture-pivot/changes.md), [Task 008](agents/work/008-software-only-product-refocus/changes.md), [Task 011](agents/work/011-mailpit-email-delivery/changes.md), [PR template](.github/pull_request_template.md).

## License

Proprietary - Roventics Pty Ltd
````

## Original `AGENTS.md`

````markdown
# Agent Instructions

Before starting work, read:

- `agents/context.md` for Monitor scope.
- `agents/rules.md` for engineering standards and the required workflow.
- The nearest directory `README.md` for task-specific detail.

For every new task:

1. Inspect the relevant code and documentation.
2. Ask focused clarification questions before editing code; keep them visible in chat even when using option buttons.
3. Create `agents/work/NNN-short-title/prompt.md` from `agents/prompt.md` after questions are answered.
4. Paste the completed prompt into chat and get developer approval.
5. Implement only approved scope, then verify it.
6. Record results, reuse and checks in `changes.md`.

Use the next three-digit work number. Keep roadmap ticket IDs stable and each
task/PR small enough to review. Read-only Switch UI and Roventics brand reference
inspection is approved; never modify either sibling repository without explicit
authorisation.

## Product boundary

Monitor V1 is a software-only prepaid-electricity planning application. Users
manually record remaining balance and purchased top-up energy in kWh at selected
times. Use simple, tested calculations. With one actual balance, show a labelled
10 kWh/day starting assumption; use measured per-meter usage once valid intervals
exist. Without a balance show "Not enough data"; never hide inconsistent history
behind the default. V1 has no tariffs, Rand forecasts, payment execution,
hardware, OCR, MQTT or ML.

Preserve hardware/OCR research for later evidence-driven reconsideration. Any
future physical integration must not open, electrically modify, bypass or
interfere with a meter. Anomaly output is never proof of theft.

## Preservation

Before deleting retired files, check dependencies and verify recovery copies;
record exact paths and checks in changes.md. Preserve live data, backups,
research, unique design sources, refocus.md and historical work records. Never
reset a database or start/restart source services without appropriate approval.
````

## Original `agents/context.md`

````markdown
# Repository Context

Monitor is a software-only prepaid-electricity planner: email login -> named
meters -> manual balance/top-up kWh records -> transparent estimates.
The root [README](../README.md) owns stable roadmap IDs and priority. Component
READMEs hold details; historical results stay in work/ and Git.

## Next iteration (Task 089, planning only)

On 1 November 2026 the owner confirmed the deployed app works and authorized a
documentation-only plan across Switch, Monitor and a new sibling meter repository.
Current Monitor behavior still requires email login. The owner confirmed that
Ticket 68 must allow local browser saving without login. Whether to include an
explicit account transfer in the first release remains open in 68.1. No guest
code, server bypass or deployment is included.

Priority: Switch measured breadboard enclosure and physical tests first; Monitor
68/65 guest onboarding -> 57.3 deploy -> 67.1 Reddit recruitment -> 67.2 roughly
30-day feedback second; Meter problem/evidence/detection research third. Reuse
existing stable IDs; research 66 and mobile packaging 68.5 do not block guest web.
Preserve account data, roles, email auth and sharing; no implicit guest upload or
new tracking. The new Meter is research-only, distinct from Monitor's historical
meter-reading name. Future physical experiments need their own approved scope.

## Current contracts

- Task 088 formats login-code emails as compact monochrome HTML plus a plain-text
  fallback, with visible selectable codes, existing expiry, non-sharing guidance
  and Roventics footer/logo. No copy button or authentication/SMTP change. This
  completes only Ticket 70's login presentation; reminder HTML remains future work.

- Task 086 adds public homepage search metadata, robots.txt and a single-URL
  sitemap through the existing Vite public assets. Private meter records remain
  authenticated; crawl preferences are not access control. The frontend README
  records Search Console submission after deployment.

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

## Historical implementation notes

The ordering in these prior completion records is historical. Task 089's next
iteration above and the root roadmap govern new work; preserve old verification
claims only within their original scope.

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
13. Task 089 promotes guest web use under 68.1-68.4; later mobile/installable
   work remains 68.5. Today's backend remains authenticated.

## Git handoff

Task 088 was committed/pushed to master as d190374 on 25 October 2026, with
Job Talk's email presentation published separately. Task 083's shared HTTPS edge
is the current production arrangement; earlier local-only Compose statements
are superseded. The owner reports deployment working as of 1 November. This is
not an independently repeated live security/SMTP audit. Production monthly mail
remains off in the committed Compose unless separately changed/approved.

Task 089 creates planning documents only, without commit/push, source restarts,
database operations, deployment, public posting or feature implementation.

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
````

## Original `agents/rules.md`

````markdown
# Engineering Rules

## Code

- Prefer clear, junior-friendly code over clever or compressed code.
- Search for reusable functions/patterns before adding new ones.
- Extend existing code when practical instead of duplicating it.
- Keep functions focused and names descriptive; explain why in comments.
- Update tests for changed behaviour and run the smallest relevant suite.
- Do not add dependencies, change architecture or expand scope without approval.

## Python

- Add type hints to function parameters and return values.
- Add concise docstrings to public modules, classes and functions.
- Document private helpers when their purpose is not obvious.

## Review size

- Aim for at most 100 changed implementation lines per PR; tests, docs and generated files are excluded.
- Split larger work into numbered tasks. Explain necessary exceptions in prompt.md.
- Keep commits focused on one concern.

## Documentation and data

- Root README: project context and short phased ticket summaries.
- Closest component README: detailed requirements and implementation context.
- Work records: concise, factual changes, reuse and actual verification results.
- No docs directory. Docker/config files stay under software/.
- Do not commit real secrets, meter images, customer information or private bills.
- Prefer simple measured approaches. Do not call desktop tests hardware validation.
- Never label an anomaly as proof of tampering or theft.

## Task workflow

1. Read context, rules, relevant README and existing code.
2. Ask focused questions until aim, scope, reuse, checks and exclusions are clear.
   Offer clickable choices when available, but repeat essential questions in chat.
3. Allocate the next NNN-short-title directory under agents/work/.
4. Fill prompt.md from agents/prompt.md, paste it into chat and wait for approval.
5. Implement and verify only approved work.
6. Write changes.md with results, reused code and checks actually run.

Do not touch sibling repositories without explicit authorisation. Do not start
future tasks merely because their roadmap entries exist.
````

## Original `agents/prompt.md`

````markdown
# Task NNN: Short title

## Aim

One sentence describing the outcome.

## Clarifications

- Question: Answer.

## Change

- Small, specific change.

## Reuse

- Existing file, function, or pattern to reuse.

## Verify

- Check or test that proves the change works.

## Out of scope

- Work intentionally excluded from this task.
````
