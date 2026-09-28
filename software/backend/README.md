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
remains process-only and does not check PostgreSQL. The superseded Keycloak
bearer-token endpoint has been removed; authentication endpoints do not exist
until the email OTP and secure cookie-session tickets implement them. Ticket 9
adds protected latest/history queries after the access and reading models exist.

Development CORS allows only the configured `MONITOR_CORS_ORIGIN`; Compose sets
this to the loopback frontend URL. Do not broaden it without an approved client.

## Planned access boundaries

Human authentication will expose `/api/auth/request-otp`,
`/api/auth/verify-otp`, `/api/auth/logout` and `/api/me`. Request responses must
not reveal whether an email is authorised. Codes must be random six-digit
values, stored only as hashes, expire within the approved 5-10 minute window,
allow limited attempts and work once. Successful verification creates an
expiring HTTP-only cookie session with an appropriate SameSite policy and the
Secure flag outside local HTTP development; the browser must not store
credentials or sessions in local storage.

Device ingestion will use `/api/device/readings`, a device UUID and a scoped,
revocable credential. It must not accept a human cookie as device proof. SMTP
delivery stays behind an abstraction with safe development capture or console
behavior so the API does not depend directly on one provider.

Ticket 10 must enforce scoped device credentials and ownership before real
uploads. Human passwordless email sessions must never double as device
credentials.
Define units, UTC timestamps, duplicate/retry semantics, validation errors and
confidence rejection with Tickets 8-9. Do not invent missing OCR values.

Use clear typed Python with docstrings and reusable functions. Production
deployment settings are not defined yet.
