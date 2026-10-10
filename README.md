# Roventics Monitor

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
    |-- database/       # PostgreSQL and raw SQL migrations
    `-- ocr/            # deferred OCR research
```

Documentation stays in these READMEs; no `docs/` directory. Development Compose,
Docker build files and `.env.example` live under `software/`; real `.env` files
are ignored.

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
- [ ] Ticket 56: End-to-End V1 Validation — multi-user isolation, corrections, edge cases and household usability (after 55).
- [ ] Ticket 57: Deployment Preparation — production configuration, backups, operations and release checklist (after 56).
- [ ] Ticket 58: Monitor App Identity — replace the current company-led mark
  with a user-supplied, recognisable Monitor logo and retain a modest Roventics
  acknowledgement on the website. This is separate from Task 033 and begins only
  after the final logo asset is supplied and its placement is approved.

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
