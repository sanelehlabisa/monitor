# Monitor software

Planned path: image -> backend-hosted OCR initially -> REST API -> PostgreSQL ->
web UI. Device OCR remains an evaluated later option after measuring fit.

## Components

- [Backend](backend/README.md): FastAPI API and configuration.
- [Database](database/README.md): PostgreSQL, Psycopg and versioned raw SQL.
- [Frontend](frontend/README.md): React balance/history/status.
- [OCR](ocr/README.md): simple recognition of one meter from PC photo fixtures.

## Development stack (Ticket 2)

Copy `.env.example` to `.env`, change the development passwords, then run:

```powershell
docker compose -f dev.docker-compose.yaml up --build
```

The frontend is at `http://localhost:5173`, the API health endpoint at
`http://localhost:8000/health`, and PostgreSQL is available on localhost port
5432. All host bindings can be changed in `.env`; they remain loopback-only.

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

Backend and frontend source directories are bind-mounted for reload. Rebuild
after changing Python or npm dependencies. Actual `.env` files stay local and
ignored. The committed defaults are development-only and must not be exposed.

The API baseline, raw SQL migrations and Material UI shell are implemented.
Human login is deliberately inactive while passwordless email OTP and secure
cookie sessions are built in follow-up tickets. Device UUID/credential access
is a separate boundary from human login.

Planned human endpoints are `/api/auth/request-otp`,
`/api/auth/verify-otp`, `/api/auth/logout` and `/api/me`. Planned device
ingestion uses `/api/device/readings` with device credentials rather than a
human session. None of these contracts is implemented by Task 007.

After changing frontend dependencies, refresh an existing named dependency
volume before restarting the frontend:

```powershell
docker compose -f dev.docker-compose.yaml run --rm --no-deps frontend npm ci
```

Production deployment, MQTT, payment integration and OCR implementation are
out of scope. Backend-hosted OCR is the preferred first integration for rapid
iteration, not evidence of measured accuracy or device suitability. Use
consented data with explicit retention/access rules.
