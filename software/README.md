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
Ticket 48 confirmed active runtime code has no obsolete device/OCR integration.

After changing frontend dependencies, refresh an existing named volume:

```powershell
docker compose -f dev.docker-compose.yaml run --rm --no-deps frontend npm ci
```

## V1 product boundary

Users manage nickname-only meter/property profiles and manually enter actual
balance and top-up energy in kWh. V1 does not require a physical meter number,
tariff, Rand amount, device credential, image or OCR result. Forecasts must show
"Not enough data" until valid history supports them and must visibly distinguish
actual records from estimates.

Production deployment, payment integration, MQTT, hardware and OCR remain out of
scope until their roadmap status changes through an approved task.
