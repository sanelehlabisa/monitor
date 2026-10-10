# Monitor software

Active V1 path: manual balance/top-up kWh entry -> FastAPI -> PostgreSQL ->
deterministic forecast -> Material UI dashboard. Hardware and OCR are not active
dependencies.

## Components

- [Backend](backend/README.md): authentication, meter ledger APIs and forecasting.
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

This is image preparation only, not a ready deployment stack. Tasks 037-038
(production Compose/env and operations) remain unapproved; HTTPS is needed for
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
