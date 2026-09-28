# Backend

FastAPI REST service with a reusable application factory, typed configuration
and a process-only health endpoint. Settings use the `MONITOR_` prefix; see
`.env.example` for supported development values.

The backend connects directly through Psycopg and applies pending SQL files
before Compose starts Uvicorn. Run the suite against the development database
from `software/`:

```powershell
docker compose -f dev.docker-compose.yaml run --rm backend python -m pytest
```

`GET /health` reports the service name, version and configured environment. It
remains process-only and does not check PostgreSQL or Keycloak. `GET /auth/me`
requires a Keycloak bearer token and returns only the validated subject,
username and optional email. Ticket 9 adds reading submission and latest/history
queries after the device and reading models exist.

Development CORS allows only the configured `MONITOR_CORS_ORIGIN`; Compose sets
this to the loopback frontend URL. Do not broaden it without an approved client.

Ticket 10 must enforce scoped device credentials and ownership before real
uploads. Keycloak handles user authentication, not an assumed device password.
Define units, UTC timestamps, duplicate/retry semantics, validation errors and
confidence rejection with Tickets 8-9. Do not invent missing OCR values.

Use clear typed Python with docstrings and reusable functions. Production
deployment settings are not defined yet.
