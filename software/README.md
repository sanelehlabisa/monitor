# Monitor software

Active V1 path: manual balance/top-up kWh entry -> FastAPI -> PostgreSQL ->
deterministic forecast -> Material UI dashboard. Hardware and OCR are not active
dependencies.

## Components

- [Backend](backend/README.md): authentication, meter ledger APIs and forecasting.
- [Forecast research](backend/research/forecasting/README.md): isolated synthetic
  datasets, plots and a rolling-linear simulator, not an application dependency.
- [Database](database/README.md): PostgreSQL, Psycopg and versioned raw SQL.
- [Frontend](frontend/README.md): mobile-first manual entry, estimates and history.
- [OCR](ocr/README.md): preserved future research only.

## Development stack

Copy `.env.example` to `.env`, set the local administrator email list and change
the development password, then run:

```powershell
docker compose -f dev.docker-compose.yaml up --build
```

The frontend is at `http://localhost:5173`, the API health endpoint at
`http://localhost:8000/health`, Mailpit's captured-email UI is at
`http://localhost:8025`, and PostgreSQL is available on localhost port 5432.
Host bindings remain loopback-only. Mailpit's SMTP port 1025 is available only
inside the Compose network.

Stop the stack without deleting data:

```powershell
docker compose -f dev.docker-compose.yaml down
```

After updating from the former Keycloak stack, remove its obsolete container:

```powershell
docker compose -f dev.docker-compose.yaml down --remove-orphans
```

Reset all local database and frontend dependency volumes:

```powershell
docker compose -f dev.docker-compose.yaml down --volumes
```

Backend and frontend sources are bind-mounted for reload. Rebuild after changing
Python or npm dependencies. The ignored `.env` is the visible source of Compose
development values; Compose reports required missing values instead of silently
using a second set of inline defaults. The committed `.env.example` contains
development-only examples and must not be exposed as production configuration.

The API health baseline, raw SQL migrations and Material UI shell exist. Tickets
43-46 implement email OTP delivery, digest-only sessions, the human auth API and
the Material UI login flow with secure HTTP-only cookie transport. Tasks 015-018
complete raw-SQL meter profiles, authorised CRUD and signed-in user/admin meter
management. Tasks 019-022 complete raw-SQL balance/top-up persistence,
authorised nested CRUD and the mobile manual-entry/history UI. Tasks 023-026 add
one replaceable deterministic forecast model, an authorised derived dashboard
API and responsive planning estimates that retain honest unavailable states.
Tasks 027-030 complete opt-in raw-SQL reminder preferences, durable finite email
delivery, authenticated owner/admin APIs and per-meter Material UI controls.
Task 031 makes administrator testing clearer with separate owned and system-wide
meter views without changing ownership or backend access policy.
Task 032 adds server-side meter search. Task 033 widens the planning dashboard,
separates manual records into tabs and hides reminder settings in the frontend;
the backend reminder preferences and delivery runner remain available.
Task 035 adds manual dashboard refresh and honest retry states after failed
reads; retrying estimates does not repeat saved ledger writes.
Task 037 simplifies the planning card to three headline estimates and two record
buttons, with forms/history/settings shown only when requested. The backend
calculation and persistence contracts are unchanged; see the frontend README.
Task 038 adds right-aligned account navigation, linkable meter-ID pages and a
wider details/planning layout. Two retained synthetic meters under a separate
local demo user support admin testing through All meters; access instructions
are in the frontend README. No startup seeding or forecast-policy change is added.
Task 039 removes navigation branding/role badges, shortens Back, enlarges the
account icon and standardises typography/name-owner alignment. Demo histories,
admin access, routes and backend calculations remain unchanged.
Task 040 enlarges the account icon to 42px, moves selected-meter renaming into
Name/Owner key-value details and adds pencil/trash actions to each meter-list
row. Bottom Meter settings is removed; the same authorised APIs and confirmed
deletion are reused. No backend, forecast or persistent demo history is changed.
Task 041 adds consistent black section headers, compact My/All tabs and white
active-tab styling. Pencil now activates editing and changes to Save on both
pages; creation becomes the first list row and search/clear icons sit inside
the search field. Text/controls are smaller without forced uppercase. The list
uses `/meters`, while root entry links and meter-ID navigation remain compatible.
Task 043 completes the supplied Monitor logo/favicon and blue/teal theme, with
a compact brand header and small linked Roventics footer. Typography, existing
flows, forecasting and persisted data are unchanged; see the frontend README.
Ticket 48 confirmed active runtime code has no obsolete device/OCR integration.

After changing frontend dependencies, refresh an existing named volume:

```powershell
docker compose -f dev.docker-compose.yaml run --rm --no-deps frontend npm ci
docker compose -f dev.docker-compose.yaml restart frontend
```

The existing frontend dependency volume survives image rebuilds. Refresh it
after lockfile changes, then restart Vite so it loads the new dependencies.
Frontend file watching uses polling for reliable Docker Desktop bind-mount
reload. A practical local walkthrough is in the frontend README.

## Production images (Task 036 preparation)

The Dockerfiles now have named `development` and `production` targets.
Development Compose explicitly selects `development`; its commands, mounts,
ports and runtime environment values are unchanged. Build the production images
from `software/`:

```powershell
docker build --target production -t monitor-backend:production ./backend
docker build --target production -t monitor-frontend:production ./frontend
```

Production is also the default Dockerfile target. The frontend serves the built
React assets through Nginx on port 80; the backend runs Uvicorn on port 8000
without reload, as a non-root user. No local `.env*` files enter either build.
Runtime credentials must not be passed as build arguments or copied into images.

To run, the frontend needs a reachable `backend:8000` name on its Docker network.
The backend defaults to production mode and requires a unique
`MONITOR_OTP_HMAC_SECRET` at runtime. Supply the database, public origin, admin
and SMTP settings explicitly for the deployment; development defaults are not a
production configuration. SQL migrations and database setup are not performed by
the image command. See the component READMEs for the runtime boundaries.

This is image preparation only, not a ready deployment stack. Remaining Ticket 57
work (production Compose/env and operations) is unapproved; HTTPS is needed for
production cookie login. No VPS, DNS, TLS or household database changes are
included. Both production and development images built successfully after Docker
recovered. Disposable smoke checks passed for static assets, SPA fallback,
proxied API errors/cookie headers, process health and production-secret refusal.
Only task containers/network were removed; existing development services and
stored data were untouched by these checks.

## V1 product boundary

Users manage nickname-only meter/property profiles and manually enter actual
balance and top-up energy in kWh. V1 does not require a physical meter number,
tariff, Rand amount, device credential, image or OCR result. Forecasts must show
"Not enough data" until valid history supports them and must visibly distinguish
actual records from estimates.

Actual production deployment, payment integration, MQTT, hardware and OCR remain
out of scope until their roadmap status changes through an approved task.

## Planned validation and release

Tasks 042 and 050 record requirements only; they implement none of these tickets.
Usability 65 and forecasting validation 66 precede web deployment 57, followed by
personal 56 and external 67 testing. The root README owns IDs and cross-product
priority. Ticket 66's candidate research does not automatically replace the app.

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
physical device processing. Optional starting-rate defaults remain labelled
experiments; the live Not enough data policy stays unchanged. The simulator's
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

Reuse the completed Task 036 images; do not rebuild an architecture from scratch.
Plan the existing Roventics VPS/subdomain, choosing exact host/domain details in
the later approved implementation prompt. Release follows 65/66 readiness.

- Production Docker configuration without reload, minimal explicit runtime env
  and secrets, HTTPS/public origin and secure-cookie login.
- Versioned SQL migration procedure, persistent PostgreSQL data, backup schedule
  and a demonstrated restore/rollback procedure before pilot invitations.
- Real SMTP/OTP delivery with a verified request/login/logout flow; no public
  Mailpit, database or administrative debug endpoint.
- Basic service/database/email checks, actionable error logging and a simple
  privacy statement explaining stored emails, records, use and contact/removal.
  Never log OTPs, session tokens or secrets.
- Acceptance: HTTPS meter/ledger/forecast smoke checks, user/admin isolation,
  restart persistence, migration/restore evidence and an operations/release
  checklist. Deployment itself still requires separate approval.

### Ticket 67: External User Testing

After 57 and 65/66 readiness, invite 3-5 consenting internet users; personal
testing 56 runs alongside it. Record onboarding completion, repeat reading
entries, usefulness, errors/confusion, requests and continued usage over a
declared pilot period. State estimates/limitations, keep records private and
summarise findings without committing identifiable household data.
Acceptance: a small cohort feedback summary and prioritised fixes. Free testers
are usability evidence, not proof of commercial demand.

Usability/identity/PWA detail is in the frontend README; deterministic validation
detail is in the backend README. Purchase costs and cost estimates remain
deferred because the active schema accepts kWh only.
