# Monitor software

Planned path: image/reading -> OCR where selected -> REST API -> PostgreSQL ->
web UI. Task 002 provides a local development stack with placeholders only.

## Components

- [Backend](backend/README.md): FastAPI API and configuration.
- [Database](database/README.md): PostgreSQL and migration plan.
- [Authentication](keycloak/README.md): Keycloak users and separate device access.
- [Frontend](frontend/README.md): React balance/history/status.
- [OCR](ocr/README.md): simple recognition of one meter from PC photo fixtures.

## Development stack (Ticket 2)

Copy `.env.example` to `.env`, change the development passwords, then run:

```powershell
docker compose -f dev.docker-compose.yaml up --build
```

The frontend is at `http://localhost:5173`, the API health placeholder at
`http://localhost:8000/health`, and Keycloak at `http://localhost:8080`.
PostgreSQL is available on localhost port 5432. All host bindings can be
changed in `.env`; they remain loopback-only.

Stop the stack without deleting data:

```powershell
docker compose -f dev.docker-compose.yaml down
```

Reset all local database and frontend dependency volumes:

```powershell
docker compose -f dev.docker-compose.yaml down --volumes
```

Backend and frontend source directories are bind-mounted for reload. Rebuild
after changing Python or npm dependencies. Actual `.env` files stay local and
ignored. The committed defaults are development-only and must not be exposed.

The services are placeholders: API/config tests (3), migrations (4), realm
integration (5) and frontend behaviour (6) remain separate.

Production deployment, MQTT, payment integration and OCR implementation are
out of scope. Use consented data with explicit retention/access rules.
