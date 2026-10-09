# Backend

FastAPI REST service with a reusable application factory, typed configuration
and a process-only health endpoint. Core settings use the `MONITOR_` prefix;
SMTP settings use the approved Job Talk-style names in `.env.example`.

The backend connects directly through Psycopg and applies pending SQL files
before Compose starts Uvicorn. Run the suite from `software/`:

```powershell
docker compose -f dev.docker-compose.yaml run --rm backend python -m pytest
```

`GET /health` reports service name, version and configured environment without
probing PostgreSQL. Development CORS allows credentialed
GET/POST/PATCH/DELETE requests from the configured `MONITOR_CORS_ORIGIN`.

## Authentication foundation

Ticket 43 implements the storage and backend policy used by human
authentication. Any normalized email can receive a challenge. A user row is
created only after correct verification, and repeated successful logins reuse it.

Codes are random six-digit values with a 10-minute expiry, five attempts, a
60-second resend cooldown, five requests per email per hour, one-use behavior
and newest-code-wins invalidation. PostgreSQL stores only an HMAC-SHA256 digest
bound to the normalized email and challenge UUID. Per-email advisory transaction
locks serialize policy decisions. Plaintext exists only in the issuance return
value for the next delivery layer and must never be logged.

`MONITOR_OTP_HMAC_SECRET` is the only OTP policy environment setting.
Development has a clearly marked local default; production refuses to start
with it. Policy numbers stay as reviewed code constants rather than separate
environment variables.

Ticket 44 delivers each issued code through a small standard-library SMTP
boundary. Development uses Mailpit at `http://localhost:8025`; its SMTP listener
is internal to Compose. Configuration follows `SMTP_HOST`, `SMTP_PORT`,
`SMTP_SECURE`, `SMTP_USER`, `SMTP_PASSWORD` and `EMAIL_FROM`. False
`SMTP_SECURE` uses STARTTLS when the server advertises it, while true selects
implicit TLS. Credentials are never sent without encryption. Failed delivery
invalidates the challenge but keeps its row counted for request limits.

Ticket 45 exposes `POST /api/auth/request-otp`, `POST /api/auth/verify-otp`,
`POST /api/auth/logout` and `GET /api/me`. Valid-shaped OTP requests return one
HTTP 202 response for successful delivery, policy rejection or expected SMTP
failure. Verification and session failures use generic HTTP 401 responses.

Successful verification creates an expiring HTTP-only cookie session with an
appropriate SameSite policy and the Secure flag outside local HTTP development.
The browser must not store credentials or sessions in local storage. SMTP stays
behind an abstraction with isolated development capture.

Task 012 implements the persistence and domain-policy half of that session flow.
Sessions use 32-byte URL-safe random tokens, store only SHA-256 digests, expire
after a fixed 30 days and may be revoked independently. Multiple browsers or
devices may remain signed in. Invalid, expired, revoked and unknown tokens share
one domain error. Task 013 connects this boundary to `monitor_session`, which is
HTTP-only, SameSite Lax, path `/`, fixed to the same 30-day maximum age and
Secure outside local development. Logout revokes only the presented session.

## Planned product boundary

Task 015 implements raw-SQL storage for nickname-only meter profiles. The
repository supports owner-scoped CRUD plus explicit unrestricted lookups. Task
016 exposes authenticated `/api/meters` list/create and `/api/meters/{id}`
get/rename/delete routes. Regular users are always scoped to their own meters.
Emails listed in comma-separated `MONITOR_ADMIN_EMAILS` may list and manage every
existing meter; new meters still belong to the user who creates them.
Inaccessible and missing IDs share the same HTTP 404 response.

Task 019 adds raw-SQL remaining-balance storage and owner-scoped repository
CRUD. Balance kWh is non-negative with at most three decimal places. Occurrence
times are timezone-aware and unique per meter, and corrections update both the
value and time while preserving creation/update audit timestamps. HTTP exposure
arrives in Task 021.

Task 020 adds matching raw-SQL storage and scoped CRUD for purchased top-up
energy. Top-ups must be greater than zero with at most three decimals. Repeated
occurrence times are allowed because separate purchases can happen together.
This records energy already bought; it is not a payment or Rand transaction.

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
