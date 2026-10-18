# Monitor

A free, software-only electricity planning application for prepaid households.
Users manually record meter balances and top-ups in kWh; Monitor uses simple,
transparent mathematics to estimate how much electricity to add and when.

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
Sharing UI, reminder redesign and monthly planning remain separate work.
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
retained in its work record; the current user-started stack is running.

## User value

The dashboard should clearly distinguish actual entries from estimates and show:

- latest actual balance and its observation time;
- estimated current balance and daily use in kWh;
- estimated remaining days and likely run-out/next-top-up date;
- recommended top-up energy for the next 30 days; and
- simple balance and top-up history.

Until enough valid history exists, the application must show **Not enough data**
instead of manufacturing a forecast. Manual entry must take only a few seconds;
whether users return often enough is the main V1 product risk.

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
balance readings are required before deriving a consumption rate.

V1 uses deterministic calculations, not machine learning. Formula selection,
averaging windows, a conservative buffer and correction behavior belong in the
approved forecasting ticket and must be covered by examples and tests.

## Technology

- API/data: FastAPI, PostgreSQL and explicit SQL through Psycopg; no ORM.
- Identity: passwordless email OTP with secure HTTP-only cookie sessions.
- Web: React, Vite and Material UI with a mobile-first layout.
- Development: Docker Compose under `software/dev.docker-compose.yaml`.
- Reminders: opt-in monthly and predicted-low-balance email through a finite runner.

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
- [ ] Ticket 69: Database & Access Refocus — preserve existing functionality and
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
    The user-started stack passed read-only UI/API/schema smoke checks and remains running.
  - [ ] Ticket 69.5: Minimal Sharing UI — member management and membership-aware
    My/All views/search, retaining existing record-management flows.
  - [ ] Ticket 69.6: Monthly Planning Date — fixed 1st, separate from predicted
    run-out; retain current 30-day quantities and model.
  - [ ] Ticket 69.7: Shared-Member Reminders — monthly email the day before the
    1st, all meter members, per-recipient dedupe and retained low-balance rules.
- [ ] Ticket 70: Readable HTML Emails — OTP/reminder HTML with plain-text fallback
  and safe app links; reuse SMTP after 69.7's recipient/message contract.
- [ ] Ticket 65: Monitor Usability Review — first-user onboarding, clear actual
  readings/estimates, compact mobile states and wording; branding links to 58.
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
- [ ] Ticket 57: Web Deployment — reuse Task 036's completed production images;
  plan production configuration, HTTPS, migrations, OTP email, backups, monitoring,
  privacy and logging on existing Roventics infrastructure (after 65 and 66).
- [ ] Ticket 56: Personal Usage Validation — retain Task 034's completed technical
  checks; compare real household predictions with later readings and return usage.
- [ ] Ticket 67: External User Testing — a consented 3-5-user deployed pilot for
  onboarding, repeat entries, usefulness and failures; not proof of paid demand.
- [ ] Ticket 68: Future Mobile & Local-Only Use — reuse the installable-app ticket:
  guest device storage without login, optional account storage with login.
  Platform, transfer/sync and notification decisions remain future work.

### Shared execution priority

1. Database/access refocus (69.4 -> 69.7), after completed DB-role cutover and
   structure cleanup (71-73); never a reset.
2. HTML email presentation (70) after reminder semantics; complete usability (65).
3. Offline forecast research/validation (66.1 -> 66.4); 66.5 is a separate
   adoption gate, not automatic app replacement. Keep costs deferred.
4. Monitor deployment (57).
5. Begin personal (56) and external (67) testing; mobile/local-only 68 stays later.
6. While waiting for users, return to Switch's compact prototype (Switch 84).
7. Measure, design and locally print its temporary enclosure (Switch 84).
8. Complete at least two continuous weeks of internal testing (Switch 84).
9. Replace the temporary circuit after PCB arrival/bring-up (Switch 85).

Detailed dependencies and acceptance live in the [database](software/database/README.md),
[backend](software/backend/README.md) and [frontend](software/frontend/README.md)
READMEs. This ordering is planning, not batch execution approval. No existing
volume may be reset automatically; completed tickets and forecast research stay
intact. Ticket 68's new scope does not weaken today's server authentication.

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
simulator's calibrated/default rates are labelled research experiments only;
the app still shows Not enough data when required. A no-go
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
and must never modify either sibling repository.

## Documentation

- [Agent workflow](AGENTS.md), [context](agents/context.md), [engineering rules](agents/rules.md).
- [Hardware](hardware/README.md), [software](software/README.md), [OCR](software/ocr/README.md).
- [Task 007](agents/work/007-authentication-architecture-pivot/changes.md), [Task 008](agents/work/008-software-only-product-refocus/changes.md), [Task 011](agents/work/011-mailpit-email-delivery/changes.md), [PR template](.github/pull_request_template.md).

## License

Proprietary - Roventics Pty Ltd
