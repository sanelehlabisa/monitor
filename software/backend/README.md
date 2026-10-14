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

## Docker targets

`development` retains Uvicorn reload and is selected explicitly by development
Compose. The default `production` target uses the same pinned Python/dependencies
and app code, starts Uvicorn without `--reload` and runs as numeric UID/GID
10001. It defaults `MONITOR_ENVIRONMENT` to `production`, so the existing settings
validator refuses startup with the development OTP secret. Supply the unique
secret and deployment database/origin/admin/SMTP values at runtime; no credential
is built into the image. Local `.env*` files are excluded from build context.

The image command does not apply SQL migrations or create a database. Production
Compose and migration orchestration require a separate Ticket 57 task. Process health
does not validate database/SMTP connectivity. Task 036's image builds and
disposable production smoke checks passed; see the software README.

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

Task 032 adds optional `GET /api/meters?q=keyword` filtering in the raw-SQL
query. Matching is a case-insensitive literal substring across meter name and
owner email after the existing user/admin scope is applied. Missing or blank
keywords retain the complete accessible list; no client-side search, ranking or
pagination is implied.

Task 019 adds raw-SQL remaining-balance storage and owner-scoped repository
CRUD. Balance kWh is non-negative with at most three decimal places. Occurrence
times are timezone-aware and unique per meter, and corrections update both the
value and time while preserving creation/update audit timestamps. HTTP exposure
arrives in Task 021.

Task 020 adds matching raw-SQL storage and scoped CRUD for purchased top-up
energy. Top-ups must be greater than zero with at most three decimals. Repeated
occurrence times are allowed because separate purchases can happen together.
This records energy already bought; it is not a payment or Rand transaction.

Task 021 exposes nested authenticated CRUD at
`/api/meters/{meter_id}/balances` and `/api/meters/{meter_id}/top-ups`, with
entry IDs appended for get/update/delete. Inputs require timezone-aware,
non-future occurrence times and the reviewed Decimal constraints. Regular users
remain owner-scoped; configured admins may manage every meter. Foreign, missing
and meter-mismatched resources share a generic 404.

Tasks 023-024 complete the pure forecasting domain behind one public
`run_forecast_model` boundary. The initial implementation validates every
adjacent actual-balance interval, accounts for top-ups, and calculates one
time-weighted daily-use rate. It then estimates current balance, remaining days,
run-out time and the kWh needed to cover 30 days with no hidden buffer. Fewer
than two readings return `not_enough_data`; impossible history returns
`inconsistent_history`. Zero observed use remains a valid zero-rate result with
no finite run-out date. Forecast output is derived and is not stored.

Task 025 exposes `GET /api/meters/{meter_id}/dashboard`. It returns latest
actual data, separate balance/top-up records, a labelled combined newest-first
history and the current forecast result. The endpoint uses established
owner/admin scope and recalculates through `run_forecast_model` on every request;
it does not cache or persist estimates.

Task 027 adds raw-SQL per-meter reminder preferences. Both monthly and
predicted-low-balance emails default to disabled. Saved settings contain a day
from 1-28, positive low-balance lead days up to 30 and a validated IANA timezone
captured by a later browser UI. Missing rows return safe disabled defaults and
settings cascade when their meter is deleted.

Task 028 adds `python -m app.reminder_runner`, a finite command intended for an
external scheduler configured during deployment. It evaluates opted-in meters
in their saved timezone, calls only `run_forecast_model`, and sends email to the
meter owner through the existing SMTP boundary. Monthly reminders deduplicate by
local month and still request a fresh reading when no forecast exists.
Low-balance reminders require an available forecast and deduplicate by predicted
local run-out date. Durable claims prevent overlapping normal sends, recover
after 30 minutes if abandoned, and are released immediately after SMTP failure.
The command logs aggregate counts only. No background service is introduced.

Task 029 exposes authenticated GET/PATCH
`/api/meters/{meter_id}/reminders`. Missing preferences return disabled
defaults, while saved values retain the monthly day, predicted-low-balance lead
days and validated IANA timezone. Regular users remain owner-scoped and
configured administrators may manage every meter; inaccessible and missing
meters share the same generic 404. Saving settings never triggers email.

Authenticated users will create and select their own nickname-only meter
profiles, then record:

- actual remaining balance in kWh and its observed date/time; and
- manually purchased top-up energy in kWh and its purchase date/time.

API and repository queries must enforce meter ownership. V1 does not accept
device uploads, images, municipal identifiers, Rand amounts or tariffs.

HTTP consumers must call the single forecast-model boundary rather than copy its
mathematics. Estimates must include their factual basis and never be presented
as actual readings.

Use typed Python, concise public docstrings and reusable raw-SQL repository
functions. Production deployment settings are not defined yet.

## Planned Ticket 66: Forecasting Algorithm Validation

Task 042 defines the validation work only; it adds no fixtures, tests or model
changes. Reuse run_forecast_model and existing tests; use fixed, timezone-aware
synthetic datasets and manually stated expected results before public testing.
No real household dataset is yet established; demos do not prove accuracy.

Validate consumption between readings (including purchased kWh), time-weighted
daily use, estimated current balance, remaining days, run-out instant and
additional purchase for 30 days. Distinguish total 30-day usage from the extra
purchase after subtracting available balance; no hidden safety buffer.

Required dataset coverage:

- Normal consistent use and top-ups between readings, including interval edges.
- Changing consumption, missing days and irregular observation intervals.
- Invalid negative consumption, duplicate/reordered or impossible timestamps.
- Insufficient history, unusually high consumption and valid zero use.
- Elapsed time after the latest reading, later top-ups and exhausted balance.

For a fixed current time: 450 kWh 30 days earlier, a 300 kWh top-up 15 days
earlier and 300 kWh now imply (450 + 300 - 300) / 30 = 15 kWh/day.
Expected outputs are 300 kWh current balance, 20 days remaining, run-out in
20 days, 450 kWh total 30-day usage and 150 kWh additional purchase. This
example documents the existing contract; it does not add a total-usage API field.

Acceptance: deterministic expected-output examples and repeatable checks of
statuses, UTC/local equivalence, rounding and invalid/unavailable states.
Report model limitations; file small approved fixes separately if checks fail.
Optional purchase costs, tariffs and future-cost estimates remain deferred:
no such columns currently exist. Do not introduce ML, OCR or an LLM.
