# Backend

FastAPI REST service with a reusable application factory, typed configuration
and a process-only health endpoint. Settings use the `MONITOR_` prefix; see
`.env.example` for supported development values.

The backend connects directly through Psycopg and applies pending SQL files
before Compose starts Uvicorn. Run the suite from `software/`:

```powershell
docker compose -f dev.docker-compose.yaml run --rm backend python -m pytest
```

`GET /health` reports service name, version and configured environment without
probing PostgreSQL. Authentication and product endpoints are planned, not yet
implemented. Development CORS allows only the configured `MONITOR_CORS_ORIGIN`.

## Planned authentication boundary

Human authentication will expose `/api/auth/request-otp`,
`/api/auth/verify-otp`, `/api/auth/logout` and `/api/me`. Request responses must
not reveal whether an email is authorised. Codes must be random six-digit
values, stored only as hashes, expire within the approved window, allow limited
attempts and work once.

Successful verification creates an expiring HTTP-only cookie session with an
appropriate SameSite policy and the Secure flag outside local HTTP development.
The browser must not store credentials or sessions in local storage. SMTP stays
behind an abstraction with safe development capture or console behavior.

## Planned product boundary

Authenticated users will create and select their own nickname-only meter
profiles, then record:

- actual remaining balance in kWh and its observed date/time; and
- manually purchased top-up energy in kWh and its purchase date/time.

API and repository queries must enforce meter ownership. V1 does not accept
device uploads, images, municipal identifiers, Rand amounts or tariffs.

Forecasting should be implemented as small pure functions or a focused domain
module independent of HTTP and persistence. It must account for top-ups between
two actual readings, validate chronology, reject impossible consumption and
return an explicit insufficient-data state. Estimates must include their basis
and never be presented as actual readings.

Use typed Python, concise public docstrings and reusable raw-SQL repository
functions. Production deployment settings are not defined yet.
