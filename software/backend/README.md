# Backend

FastAPI REST service with a reusable application factory, direct environment
reads and a process-only health endpoint. Core settings use the `MONITOR_` prefix;
SMTP settings use the approved Job Talk-style names in [the single template](../.env.example).

## Runtime settings

Task 078 removes `settings.py`, its `Settings` object and the `pydantic-settings`
dependency. Existing modules read `os.environ` directly; there is no replacement
configuration class/module or extra `.env` loader. Ten runtime values remain
required before app import/startup:

- `MONITOR_ENVIRONMENT`, `MONITOR_DATABASE_URL`,
  `MONITOR_CORS_ORIGIN` and `MONITOR_OTP_HMAC_SECRET`.
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_SECURE`, `SMTP_USER`, `SMTP_PASSWORD`
  and `EMAIL_FROM`.

Task 078's production builds, 218 backend checks, unchanged OpenAPI and isolated
HTTPS login/meter/forecast/logout flow pass. Rebuild the backend to load this
change; the running app was preserved during verification.

Missing variables fail by name rather than selecting development defaults.
Origin, OTP, SMTP and cutoff validation stay beside their consumers, with errors
that do not reflect private input values. Never print rendered Compose secrets.
Explicit blank `SMTP_USER`/`SMTP_PASSWORD` remain
valid for local Mailpit. Only `MONITOR_MONTHLY_REMINDERS_ACTIVATED_AT` is optional;
missing/blank keeps it off, while an existing saved cutoff must be preserved.

Both Compose modes map the single ignored `software/.env` into runtime variables.
They derive the database URL from PostgreSQL values and fix `MONITOR_ENVIRONMENT`
internally. Task 075's development Compose fixes local CORS and Mailpit SMTP,
ignoring production URL/mail values. Production maps `APP_BASE_URL` to
`MONITOR_CORS_ORIGIN` and the frontend's internal origin setting. Use
`APP_BASE_URL=https://monitor.roventics.com` for the shared production HTTPS edge.
Both files run directly through Compose; no binding variables are needed.
Do not add duplicate mode/CORS/database URL keys or log-level settings to `.env`.
Pydantic remains for API request/response schemas, pinned to the existing runtime's
`2.13.5` version to preserve the OpenAPI contract during this cleanup. Production
requires an HTTPS origin, a unique OTP secret and real SMTP credentials, including
when run locally. Production reminders stay off; access-log policy is unchanged.

## Code layout

```text
app/
  main.py          application factory; app.main:app stays the entrypoint
  database.py      Psycopg connection helpers
  __init__.py      package version
  modules/         existing domain logic, raw SQL, email and forecast calculations
  schemas/         Pydantic requests/responses and their existing validators
  endpoints/       auth, meters, ledger and reminders HTTP routers
```

Domain dataclasses stay with their modules; schemas are not ORM models. Packages
have docstring-only initializers, without compatibility shims or eager exports.
All callers still use `app.modules.forecasting.run_forecast_model`; this layout
does not change calculations, API paths/payloads, access rules or cookies.
Task 061 passed all 67 isolated backend checks; canonical OpenAPI is identical
to Task 060, and independent AST checks found no function-body changes.

## Database setup and checks

The backend connects directly through Psycopg. Empty-volume initialization runs
`schema.sql` then `seeds/010-users.sql` in both modes, provisioning only the
approved admin. Development also runs `seeds/020-demo-meters.sql`; production
never seeds meters or history. Existing volumes do not replay these files.
Compose starts Uvicorn without running or
mounting numbered migrations. Integration checks no longer apply migrations.
Run checks only inside a dedicated verification environment with an explicitly
isolated `MONITOR_DATABASE_URL` and initialized schema, never the current DB.
Supply all ten synthetic runtime settings above before starting pytest:
test collection imports the app and will now fail clearly without them. Point
SMTP only at isolated capture; do not load the current installation's `.env`:

```powershell
python -m pytest
```

Keep MONITOR_MONTHLY_REMINDERS_ACTIVATED_AT blank for ordinary isolated checks;
lifecycle tests explicitly enable only their disposable DB/Mailpit environment.

Task 059 safely upgraded the existing volume. Retired SQL and the legacy CLI
are no longer active files; the [database README](../database/README.md) records
verified recovery copies. Never replay fresh setup against an existing volume.
Task 058's 64 backend checks passed against the current bind-mounted code using
the cached backend image; installed versions matched requirements. Fresh/copy-
upgrade, persistence, both reload paths and source-preservation/cleanup passed.
A network-disabled fresh image build failed because required pip cache
was unavailable; no dependency change or successful fresh build is claimed.

`GET /health` reports service name, version and configured environment without
probing PostgreSQL. Development CORS allows credentialed
GET/POST/PATCH/DELETE requests from the configured `MONITOR_CORS_ORIGIN`.

## Docker targets

`development` retains Uvicorn reload, limited to `app/` so the isolated research
environment is not scanned, and is selected explicitly by development Compose.
The default `production` target uses the same pinned Python/dependencies
and app code, starts Uvicorn without `--reload` and runs as numeric UID/GID
10001. The image explicitly sets `MONITOR_ENVIRONMENT=production`; environment
reads have no installation defaults. The OTP module still refuses
the example development OTP secret in production. Supply the other required
runtime settings, including a unique secret; no credential is built into the
image. Local `.env*` files are excluded from build context.

Task 078 left running containers on their previous image. The user subsequently
rebuilt the backend; Task 079 confirmed the removed settings file was absent.

The image command does not install/upgrade SQL or create a database. Production
Compose keeps private PostgreSQL and SMTP egress. Uvicorn trusts proxy
headers only from the private web subnet;
the production gateway supplies its configured canonical Host/HTTPS scheme and
removes client forwarding headers. Keep the trusted CIDR aligned with Compose
IPAM if adapting the network after a collision check. Production monthly reminders
are forced off pending separate activation, regardless of any local cutoff.
There are exactly development and production Compose files. From `software/`,
run `docker compose -f prod.docker-compose.yaml up --build` after shared-proxy
setup. Production exposes neither backend nor database on host ports. Its
frontend serves HTTP80 privately, joins `roventics_proxy` as `monitor-frontend`
and has a `127.0.0.1:8082:80` diagnostic binding. The shared Roventics edge handles
public HTTP80/HTTPS443. The browser uses same-origin `/api` through both proxies;
only development publishes backend8000. See the
[production operator guide](../nginx/README.md); live deployment remains Ticket
57.2. Process health does not validate database/SMTP connectivity. Task 036's image builds and
disposable production smoke checks passed; see the software README.

## Authentication foundation

Ticket 43 implements the storage and backend policy used by human
authentication. Any normalized email can receive a challenge. Open signup
creates a user after correct verification; repeated successful logins reuse it.
Authorized sharing may provision a regular account first, but cannot authenticate
it or bypass OTP. Fresh seeds provision accounts without credentials or
sessions: they still require ordinary email OTP verification to sign in.

Codes are random six-digit values with a 10-minute expiry, five attempts, a
60-second resend cooldown, five requests per email per hour, one-use behavior
and newest-code-wins invalidation. PostgreSQL stores only an HMAC-SHA256 digest
bound to the normalized email and challenge UUID. Per-email advisory transaction
locks serialize policy decisions. Plaintext exists only in the issuance return
value for the next delivery layer and must never be logged.

`MONITOR_OTP_HMAC_SECRET` is the only OTP policy environment setting.
The example explicitly supplies a clearly marked local value, not a backend
fallback; production refuses to start with it. Policy numbers stay as reviewed
code constants rather than separate environment variables.

Ticket 44 delivers each issued code through a small standard-library SMTP
boundary. Development uses Mailpit at `http://localhost:8025`; its SMTP listener
is internal to Compose. Configuration follows `SMTP_HOST`, `SMTP_PORT`,
`SMTP_SECURE`, `SMTP_USER`, `SMTP_PASSWORD` and `EMAIL_FROM`. False
`SMTP_SECURE` uses STARTTLS when the server advertises it, while true selects
implicit TLS. Credentials are never sent without encryption. Failed delivery
invalidates the challenge but keeps its row counted for request limits.

Task 088 adds a compact monochrome HTML alternative to the login email while
retaining plain text. The contiguous code is selectable, its existing expiry is
shown, and short guidance says to use it personally and never share it. A small
Roventics logo/team/company footer uses public HTTPS assets and links, with text
remaining readable when images are blocked. No custom copy button, code-bearing
URL, new setting or SMTP/authentication behavior is added.

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

## Current backend access and forecasting

Task 063 implements membership-based code. Task 064 safely applied its reviewed
existing-data transition after a fresh backup/restore/rehearsal. The app startup
then failed Docker's health gate: the app started successfully, but its probe
repeatedly exceeded the 3-second timeout. Task-started apps were stopped.
A separately approved bounded backend-only retry passed host /health 200 and
Docker health unchanged, then stopped again. Exact probe wall times were
1.52/1.88s including Docker CLI overhead; the new native health sample was 1.29s.
The earlier timeout did not recur in that diagnostic; its cause is not proven
and no fix was applied. The user subsequently started the full stack. Read-only
HTTP/schema checks passed, API bytes/dependency pins match the approved code,
and all four services were left running. A transient preflight health-state
rejection was observed before the passing run; uninterrupted health is not claimed.
Live OTP/write/browser validation remains outstanding.
All 90 isolated backend checks passed; API comparison found only three new
member operations and their response schema, with existing payloads unchanged.

- `users.type` is the sole admin authority, read on every authenticated request.
  Members manage their meter; admins manage all meters without automatic membership.
  Inaccessible/missing resources share generic 404 responses.
- `/api/meters` supports list/create; `/{meter_id}` supports get/rename/permanent
  delete. Creation atomically records creator membership. Any member/admin may
  permanently delete a whole meter/history; leaving removes membership only.
- `GET/POST /api/meters/{meter_id}/members` lists/shares by email; POST returns
  `{user_id,email}` identically for existing/new accounts. DELETE with a member
  user ID removes membership; the last member cannot be removed (409), even by
  an admin. Parent locks and separate access rechecks serialize removal/deletion
  with member changes and ledger writes.
- Sharing normalizes/validates email and creates a missing regular account in the
  same transaction as membership. It never overwrites an existing type, creates
  a session, sends an invitation or exposes a global user directory. A correct
  OTP is still needed to sign in, including for provisioned accounts.
- Optional `GET /api/meters?q=keyword` performs scoped case-insensitive literal
  substring search over name/member emails in SQL, without duplicate meters.
  Blank keywords retain the accessible list. No ranking/pagination is implied.
- Task 065 adds optional `mine=true` to that same endpoint: current memberships
  for admins too, combined with `q`. Omitted/false preserves the existing default
  (all for admins, current memberships for regular users). It reuses membership
  SQL; no additional payload, role, schema or forecast change is introduced.
  All 92 isolated backend checks pass; OpenAPI differs only by this query option.
- Creator fields (`user_id`/`owner_email`) and creator-name uniqueness remain
  compatibility metadata, never permission overrides. Task 065 labels these
  Created by and provides on-demand sharing with membership-based My in the UI.

Nested balance/top-up CRUD and dashboard/reminder settings all use the same
member/admin access. Balance kWh is non-negative; purchases positive; both allow
at most three decimals and timezone-aware non-future occurrence times. Actual
balances have unique per-meter times; purchases may share times. Nested IDs are
authorized together with their parent, retaining generic inaccessible errors.

All forecast callers still use `app.modules.forecasting.run_forecast_model`.
Task 080 uses DEFAULT_DAILY_USAGE_KWH (10 kWh/day) with exactly one actual balance
at or before calculation time. Adjacent intervals from two or more readings include
top-ups and yield one measured time-weighted daily rate. Without a balance, estimates are unavailable;
inconsistent history stays unavailable and never falls back. The existing
available status with intervals_used=0 identifies a default estimate; UI and
monthly email label this assumption. Legacy low-balance warnings require measured
intervals. Later purchases and elapsed time affect current estimates as before.
Zero observed use has no finite run-out date. Dashboard output is derived,
not stored, and includes actual records and latest actual reading/time.
Task 066's additional monthly purchase is
`max(0, rate * planning_days - current estimated_balance)`, not total usage or a
projection of balance at the future 1st. The target is the strictly-next UTC
month-start (even on the 1st); days come from its full datetime interval to the
following month-start. Rate/current-balance/run-out and unavailable states stay.
The response now uses `recommended_monthly_top_up_kwh` instead of the removed
`recommended_top_up_30_days_kwh`. `planning_at` and `planning_days` are known even
without enough history; unsupported energy/rate estimates remain null.
Task 081 additionally returns monthly_requirement_kwh: rate * planning_days,
rounded to 0.001 kWh, independent of balance. It is zero for observed zero use
and null for unavailable forecasts. The existing extra purchase and reminders
keep their current-balance subtraction.

Reminder GET/PATCH retains existing disabled-by-default settings, day 1-28,
lead time up to 30 days and saved IANA timezone. Saving never sends mail.
The finite `python -m app.modules.reminder_runner` remains a manual-only,
opt-in/creator-only legacy path, and sends only while that creator is still a member. It skips stale
removed/deleted candidates and rechecks before SMTP under the meter lock.
Monthly/low-balance eligibility, dedupe/retry rules and SMTP boundary remain;
SMTP is not transactional and crash retries are not exactly-once delivery.
Never invoke the CLI, even with --help, as an application smoke check.

Task 069's app-owned scheduler instead calls the guarded monthly member pass.
It uses the optional saved MONITOR_MONTHLY_REMINDERS_ACTIVATED_AT timestamp, not
legacy per-meter preferences. Blank disables; explicit aware ISO datetime enables
and normalizes to UTC; invalid/naive/numeric values reject. Preserve an existing
installation's cutoff across restarts. No new DB table, schema startup or user setting.

Fresh/upgrade targets restrict deletion of users still referenced as creator or
member, preventing accidental shared-data cascades. Explicit meter deletion
still cascades through its history/memberships. There is no account-deletion API,
transfer workflow or trigger. Task 064 already applied the work-record upgrade
SQL once; do not replay it or restore automatically. Current source services
are user-started and must not be restarted/stopped as a verification shortcut.

Use typed Python, concise docstrings and reusable raw SQL. No ORM, device uploads,
tariffs, Rand amounts, payment, model adoption or production deployment is added.

## Ticket 69: Database and Sharing Simplification

Task 056 is documentation-only planning. Each implementation needs a separately
approved prompt. Tasks 057/058 cover recovery and bootstrap only; no current-DB
upgrade, reset, seed or email send is authorized by them. Keep OTP/session APIs,
raw Psycopg repositories, meter/ledger
routes, finite reminder runner, SMTP boundary and `run_forecast_model`.

Dependencies: [database Tickets 69.1/69.2](../database/README.md) establish the
audited schema, backup/restore gate and fresh-setup seed before 69.3/69.4.
Task 058 introduces constrained `users.type` (default `user`) and `user_meters`
with user/meter composite PK, cascading FKs and meter-first index. Original owner
columns/queries remain the compatibility bridge. Task 058 left runtime roles and
the current volume unchanged; Task 059 now uses stored roles. Task 063 code uses
membership access; Task 064 applied its FK/backfill transition with all data
preserved. Read-only checks on the later user-started stack passed; it stays running.
The earlier approved source upgrade/one-time assignment
followed a new verified backup and isolated rehearsal before source execution.
[Frontend Tickets 69.5/69.6](../frontend/README.md) consume the resulting access
contract. Task 066 implements actual-calendar-month purchase planning
instead of fixed 30 days, using current balance without projecting it to the 1st.
Keep daily-rate/run-out logic and the research Ticket 66 adoption gate unchanged.
Keep existing clients working through the schema/access transition; do not
activate a membership-only schema or reminder contract before its dependent
backend/UI changes are ready and checked together.

### Ticket 69.3: DB-Only User Types (Task 059; complete)

Depends on: 69.1/69.2's agreed user schema and fresh-setup path.

- Store constrained `users.type` values `user` and `admin`; this DB value is the
  sole role authority. Resolve it for every authenticated request, including
  `/api/me`, rather than trusting a role cached in a cookie or matching an email.
- Keep OTP signup open. Correct verification creates a regular `user` unless
  that account already exists; repeated login preserves its stored type.
  Preserve digests, expiry, abuse controls and opaque cookie sessions.
- Seed `hlabisasanele730@gmail.com` as admin only during the approved fresh
  setup. This grants no password, OTP bypass or runtime email privilege. A
  restart or repeat login must not undo a manually changed DB role.
- Remove all admin environment settings and dependencies, including
  Compose/examples, settings and role checks. There
  is no bootstrap-admin env, env fallback or hardcoded-email runtime override.
  Later promotions/demotions are manual DB operations, not a new API/UI.

Acceptance: new and returning OTP users retain the correct DB type; a role
change affects the next request using an existing session. Admins retain full
meter access and regular users do not gain it by email/configuration. Check
fresh seeding, preserved manual demotion and removal of admin-env references.
Task 059 verified a new backup/restore and exact rehearsal, then upgraded the
current database and promoted only the existing approved admin identity. The
other account remains `user`; no source account/OTP/session creation, seed replay
or emails occurred. The changed service preflight was resolved by explicit
approval to stop only frontend/backend/Mailpit; they stayed off then, with the same
source DB kept running. Original records and both migration histories survived.
All 68 backend checks passed on an isolated fresh DB/Mailpit using current code
and cached dependency versions matching requirements. No fresh-image build is
claimed. Admin configuration is removed from active settings/Compose/examples
and the local admin key only; other local values were preserved. Stopped
containers may retain old env metadata, which is never a privilege fallback.
Source verification used SQL/private inventory; new code was checked against the
restored clone. No source HTTP login/session test was performed. Task-owned
containers/volumes/network were removed after identity checks; backups remain.

Later role changes are privileged manual DB operations, not a new API/config.
Confirm the database/account first and pass `email`/`new_type` as psql variables
(`new_type` is `user` or `admin`), never concatenate them into SQL:

```sql
BEGIN;
UPDATE monitor.users SET type = :'new_type'
WHERE email = LOWER(BTRIM(:'email'))
RETURNING id, type;
```

In the same session, `COMMIT` only after exactly one expected row is returned;
otherwise `ROLLBACK` and investigate. Never insert an absent account or replay
seeds. Promotion/demotion affects backend authorization on the next request using
the same session cookie; login/restart does not undo the stored choice.

### Ticket 69.4: Membership Persistence and Backend Authorization

Depends on: 69.1/69.2's membership schema and 69.3's DB role authority.

- Replace ordinary-user owner scope with membership scope. Create a meter and
  its creator membership atomically. Every member may manage that meter's
  readings, top-ups and membership; DB admins retain global access without
  becoming members automatically.
- Apply the same server-side scope to every protected meter path: list/search,
  detail/rename/delete (subject to the agreed deletion policy), nested ledger
  CRUD, dashboard, reminder settings and membership operations. Authorize
  parent meter and nested record IDs together; keep
  generic missing/inaccessible responses and backend keyword filtering.
- Prevent removing the last member. Serialize/check membership changes within
  the transaction so concurrent removals, leaving and account-deletion paths
  cannot orphan a meter. Account deletion must not cascade-delete a shared
  meter or its ledger merely because the departing account was its creator or
  former owner; handle a last membership explicitly before deleting the user.
- Task 063 settles permanent deletion for any current member/admin and sharing
  by normalized email with automatic regular-user creation. No invitations or
  session bypass. Retain creator metadata; 69.5 handles minimal sharing display.
  Task 064's live FK/backfill transition and running-stack read-only checks passed.
  The initial health-timeout history does not justify replaying SQL.

Acceptance: two members can manage one meter while a non-member cannot reach
any of its protected resources, including nested IDs and search results.
Removal takes effect on the next request. Check DB-admin access, atomic
creation, sequential/concurrent last-member guards and account deletion without
accidental shared-data loss. Reuse existing APIs/error conventions where useful;
69.5 owns the minimal MUI integration.

### Ticket 69.6: Calendar-Month Planning (Task 066)

Reuse run_forecast_model, its current balance and Decimal/time helpers. Always
choose the strictly-next UTC month-start, including when now falls on the 1st.
Calculate its duration to the following UTC month-start; recommend
max(0, daily_rate * period_days - CURRENT estimated balance). No balance depletion
to the future 1st, new model, calendar-month training or fabricated estimates.
Example: 15 kWh/day with 300 kWh left gives 120 kWh extra for 28-day February.

The coordinated dataclass/schema/frontend/message contract uses
recommended_monthly_top_up_kwh, planning_at and planning_days; the old 30-day
key is removed rather than silently changed or retained as a duplicate alias.
Preserve learned-rate/current-balance/run-out calculations and invalid/zero states.
No SQL, live-mail, scheduler or source-service action is included in Task 066.
Prompt: [Task 066](../../agents/work/066-calendar-month-planning/prompt.md).
All 109 isolated checks pass. OpenAPI differs only by the approved recommendation
rename and required planning metadata; dependency pins are unchanged. No live
fixture/mail or schema action occurred; exact task-owned test resources are removed.

### Ticket 69.7: Automatic Month-End Email to Meter Members

Depends on: 69.3/69.4's roles/memberships and 69.6's fixed planning date.

- Send the monthly planning email at 09:00 UTC on the last calendar day, to every current
  member of that meter initially, with no per-member opt-in or schedule
  selector. This replaces the current owner-only, default-disabled monthly
  opt-in contract, not merely its recipient query. This is not every registered
  account. Global admin access alone does not make an admin a recipient; an
  admin receives only as a member.
- Use one UTC calendar/clock policy, not device or legacy saved timezones.
  Persist per-recipient/cycle pending/sent status. On backend startup and later
  passes, recover unsent work from the DB rather than skip it after month-end.
  Discover only the latest missed cycle; already-saved pending jobs from all
  cycles still retry. Use current members, including newly shared users;
  user_meters has no joined_at. Require an explicit fixed activation cutoff and
  exclude cycles before a meter existed. Do not silently replay pre-feature
  history, reset sent records or fan out to nonmembers.
- Deduplicate monthly delivery per meter, recipient and target planning cycle:
  a December 31 send for January 1 belongs to the January cycle. Check month
  lengths, leap years and year boundaries; do not key it only by send month.
- Extend existing durable claims to recipient-level monthly delivery.
  One recipient's failure/retry must not resend successful recipients;
  removal ends future eligibility, including rechecking membership before a
  pending send. Retain failed new monthly jobs as pending and recover abandoned
  claims after the existing 30-minute lease, without claiming exactly-once SMTP
  delivery across crashes. Commit the whole selected fan-out before SMTP and
  each recipient's result independently, with claim-ownership checks and consistent
  meter-before-delivery locking. Retain a delayed job's original cycle key; use a
  fresh forecast and label its current planning date separately from the delayed
  notification cycle. Never suppress the next real cycle by rekeying a retry.
- The user confirmed monthly planning only for completion of Ticket 69. Defer
  shared/automatic low-balance warnings; preserve existing creator-only opt-in
  code, eligibility and history without scheduling it. Do not turn on extra alerts
  or claim their fan-out is complete. A monthly email may request a fresh actual
  reading when forecasts are unavailable. Keep estimate labels and warnings;
  Monitor never buys electricity or guarantees a forecast.

Split into separately approved small tasks:

- 69.7.1: durable member/cycle dispatch, missing/failed job recovery and recipient
  deduplication, using isolated SMTP only. Preserve low-balance behavior unless
  its prompt explicitly changes it; do not turn on extra alerts silently.
  [Task 068](../../agents/work/068-durable-monthly-reminders/changes.md) completes
  this finite slice. `app.modules.monthly_reminders.run_monthly_reminders` owns
  connection/commit boundaries and requires an aware activation cutoff; no caller
  transaction is silently committed.
  Reuse the existing delivery schema with target `YYYY-MM:userID` keys. Task 068
  did not wire automatic calls; Task 069 subsequently connects only app lifecycle,
  not the legacy CLI, imports or requests.
  Legacy rows/CLI keep their existing behavior: old plain YYYY-MM keys identify
  send months, not necessarily target months, and cannot be silently reinterpreted.
  All 134 isolated backend checks pass, including 25 new calendar, durability,
  concurrency and failure-isolation cases. Real internal SMTP captured three
  messages to two synthetic members, excluded admin-only access and sent none on
  repeat; delayed-cycle/current-planning dates and unavailable prompts are checked.
  OpenAPI is byte-identical to Git HEAD and pinned dependencies are unchanged.
  No source DB queries/writes, mail or service actions occurred. New-path header
  normalization and date-range failure isolation do not change live forecast math.
- 69.7.2 (Task 069; complete for monthly-only/local Mailpit): lifecycle-owned
  asyncio task, sequential passes with blocking DB/SMTP
  work off the event loop, startup recovery, cross-process overlap protection,
  bounded operations and safe shutdown/draining. Reuse the finite pass and SMTP;
  no extra scheduling service/dependency or request-triggered-only mechanism.
  Source activation needs explicit approval: hot reload of main.py could otherwise
  start sending immediately into the current stack.
  First agree/persist the fixed cutoff and reconcile legacy pending/sent records
  without dropping pending mail or inventing cross-format deduplication. Task 068
  alone does not complete legacy backlog recovery or authorize activation.
  [Task 069](../../agents/work/069-automatic-monthly-reminders/changes.md) implements
  the optional saved cutoff in ignored `.env`/Compose, immediate startup recovery
  and sequential 60-second off-event-loop passes. Stop checks roll back incomplete
  discovery and drain actual workers instead of treating thread cancellation as
  a stopped send. Reminder-owned DB connect/statement limits are 5 seconds; lock
  limit 2 seconds. SMTP retains 10 seconds per operation, not total-send time.
  Backend shutdown grace is 120 seconds. Unknown monthly keys block each automatic
  pass before claims; no jobs/history are remapped or silently dropped.
  All 157 backend/43 frontend checks and production asset build pass; API and pins
  are unchanged. Isolated real SMTP/app lifespans verify pending recovery, no restart
  duplicates, disabled mode, responsive requests and clean shutdown.
  Approved local gates found zero saved deliveries and pinned internal Mailpit
  with no relay/auth. One backend-only recreation activated the saved cutoff;
  database/frontend/Mailpit and volumes stayed unchanged. Health/proxy checks pass,
  with zero source delivery rows and no forced/external mail, backup or schema work.
  Production/external SMTP activation remains separately approved Ticket 57 work.

Acceptance: isolated multi-member fan-out, non-member/admin-only exclusion,
membership removal, recipient retries/dedup, restart/catch-up, failed/stale claims,
month/year boundaries and unchanged forecast eligibility. No real mail, source
SQL or service actions before separate approval. Explain automation in the UI
without adding settings. Reminder HTML presentation remains Ticket 70.

## Ticket 70: Readable HTML Email and App Links

Task 088 completes login-code HTML/plain formatting only. Six focused MIME,
escaping and mocked SMTP/TLS checks pass; synthetic desktop/phone HTML previews
were inspected. No real email was sent. Reminder formatting and app-link behavior
below remain planned, and real inbox-client acceptance remains an operator check.

Separate presentation ticket after the 69.7 recipient/scheduling contract; reuse
existing OTP delivery, reminder runner and SMTP abstraction. Do not redesign
authentication or change forecast math to format a message.

- Give OTP and both reminder types concise, readable HTML with a plain-text
  fallback. Escape meter names and all other inserted user-controlled content;
  retain the OTP's reviewed expiry/security guidance and honest forecast states.
- Build links from a trusted public app origin agreed in the implementation
  prompt. Reminder links may target `/meters/<id>`; normal OTP login and backend
  authorization still apply. Do not put OTPs, session tokens or new magic-login
  credentials in URLs, and do not derive links from untrusted request input.

Acceptance: inspect both MIME alternatives in Mailpit, including long/escaped
names, unavailable estimates and mobile-readable messages. Follow links while
signed out, as a member and as a non-member; verify normal login return/access
checks, trusted origins and absence of secret-bearing URLs. No real recipient
send or extra mail service is required.

## Planned Ticket 66: Per-Meter Forecast Research and Validation

Task 050 expands the existing Ticket 66 into five ordered subtickets. This is a
plan only: it adds no datasets, plots, tests, candidate code or live-model changes.
Each implementation needs its own small approved task. Synthetic results are
not household validation; Tickets 56/67 remain necessary after deployment.

Task 051 implements an initial generator/plotting slice in
[research/forecasting](research/forecasting/README.md). Matplotlib is isolated in
research requirements/a local environment, not runtime requirements or images.
Research and generated outputs are excluded from the Docker build context. Both
66.1 and 66.2 remain open for their full acceptance work. Task 052 adds a separate
single-script rolling-linear simulator with initial chronological error exports.
Task 053 simplifies its current interface/generation: one nominal 10 kWh/day
household and a Low/Mid/High randomness slider. The earlier utilities were
archived before retirement. Task 055 removes the focused check script after
local backup at the user's request; simulator.py is the current entrypoint.
It defaults to 730 replay days and a nominal 0.1-second timer interval, shading
recent 60/90-day context orange in both plots. The forecast remains 30 days,
not a reliable two-year prediction. Headless/native GUI smoke checks passed;
no removed research test suite was rerun.
Task 053's historical 20 focused checks, headless
exports and native GUI verification passed. Task 052's results
remain historical, not the changed generator's accuracy. The current 66.3 scope
is still one rolling line, not segmentation or live-model replacement. NumPy
joins Matplotlib only in research requirements. Full
validation/go-no-go and separately approved application integration remain open.

The live model already recalculates from one meter's history, using total
observed consumption divided by total elapsed days. Keep `run_forecast_model`
and its existing tests as the baseline; do not pool users' histories. The API
and reminder repositories enforce meter scope before calling this pure function.

Research contracts shared by all subtickets:

- Use synthetic kWh only, stable distinct meter IDs, recorded seeds/configuration,
  timezone-aware UTC instants and explicit Decimal/rounding rules.
- Count top-ups in `(previous reading, current reading]`; purchases exactly at
  the previous reading are excluded and those at the current reading included.
  Later purchases known by `as_of` affect projected balance, not past usage.
- Keep sparse observed balances/top-ups separate from dense hidden usage truth.
  Never invent hourly observations or silently repair impossible records.
- No real/demo DB writes, runtime/API changes or heavy frameworks. Research-only
  Matplotlib/NumPy do not change backend dependencies. Hardware/OCR/ML,
  costs and payments stay deferred.
- The live app uses Task 080's labelled fixed 10 kWh/day assumption with one
  balance and retains `not_enough_data` without a balance. Research-calibrated
  defaults and rolling regression remain separate experiments, never actual
  meter readings or deployed learned rates; their adoption needs separate approval.

### Ticket 66.1: Reproducible Synthetic Meter Datasets

Depends on: the existing ledger/forecast contracts; no model change.

Outputs: a small reproducible dataset generator, its seed/configuration manifest,
distinct meter profiles, separate observed/truth files and expected example results.

- Cover steady low/high use, changing use and a weekly pattern. Sample the same
  profiles with daily, weekly and irregular manual readings, including long gaps.
- Include a 30-day worked example and longer histories with a full held-out
  30-day horizon; do not score beyond the available hidden truth.
- Include purchased kWh, several purchases between readings, exact interval-edge
  purchases, elapsed time after the last reading and later known purchases.
- Add labelled cases for insufficient history, zero/high use, exhausted balance,
  negative inferred consumption, duplicate times, reordered inputs and future or
  timezone-naive timestamps. Invalid cases must stay distinguishable from valid.

Acceptance: reruns reproduce values/IDs and sampling; valid histories conserve
energy and match hand-calculated intervals within documented rounding. Changing
another meter's data cannot affect a meter's inputs. Hidden truth is unavailable
to the forecasting adapter; no generated fixture is inserted into the app DB.

### Ticket 66.2: Consumption Transformation and Visualisation

Depends on: 66.1's checked datasets and observation/truth separation.

Outputs: one reusable transformation, labelled plots and a short rebuild/readme
explanation; keep visualisation offline, not a new application screen.

- Calculate cumulative consumed energy at each real observation:
  `consumed(t) = initial balance + purchases in (initial time, t] - balance(t)`.
- Plot observed balance/top-up events and adjusted consumption against actual
  elapsed time. Fit consumption, not the saw-tooth balance jumps from purchases.
- Distinguish observations, inferred connecting segments and hidden evaluation
  truth visually. Sparse intervals identify average use, not hourly behaviour.
- Surface invalid chronology/consumption rather than clipping it into plausible
  data. Reordered valid inputs may be sorted explicitly, preserving source facts.

Acceptance: transformed intervals match 66.1's expected consumption, including
boundary purchases and UTC-equivalent timestamps. Plots cannot misrepresent
interpolation as a measured reading or expose hidden truth to candidate inputs.

### Ticket 66.3: Rolling Linear Simulator and Baselines

Depends on: 66.1/66.2; retain the unchanged live method for comparison.

Outputs: simulator.py, readable equations,
two-graph replay, PNGs and JSON/CSV error summaries. Task 053 simplifies 052's
interface/generation without replacing its single-line forecasting algorithm.
That experiment supersedes the segmented scope originally planned by 050.

- Fit one ordinary least-squares `y = mx + c` to reconstructed consumption at
  actual balance times in the latest 90 days, optionally 60. Use actual elapsed
  days, never invented hourly readings, segments, blending or periodic models.
- Require two distinct valid in-window readings for a fitted rate. Otherwise,
  when a balance exists, show the explicitly assumed frozen starting rate.
  Calibrate that rate as the median of separate fictional training households'
  consumption/elapsed-day ledger rates. Training IDs/seeds/parameters are separate
  from demo households, and calibration does not change with demo duration,
  randomness, lookback or reset. Fixed 10 kWh/day is the labelled initial/fallback
  and comparison. None of these defaults changes the live app's cold-start policy.
- Reconstruct with purchases in `(previous reading, current reading]`. Reject
  inconsistent or non-finite inputs; never hide them with a default. Zero use
  is valid, with no finite run-out. No recorded balance means no prediction.
- Anchor current/future balance to the latest actual reading plus known later
  purchases minus estimated use, not the fitted intercept. Predict the next
  30 days with no buffer; future balance assumes no further purchases. Distinguish
  total 30-day consumption from additional kWh after the remaining balance.
- Default to 730 fictional replay days at a nominal 0.1-second timer interval
  plus rendering overhead (CLI-adjustable). This is not a two-year forecast;
  the future horizon stays 30 days.
  One household keeps a nominal 10 kWh/day basis across Low/Mid/High levels;
  randomness changes daily-use variability and purchase-interval jitter, not
  average-usage classes or missed top-ups. The bounded purchase policy prevents
  outages; it does not validate physical exhaustion.
- GUI shows exactly two graphs (balance and total consumption), three headline
  estimates (current balance, remaining days and predicted monthly requirement
  for 30 days), a small date/source label, Play/Pause/Reset and one bottom
  randomness slider.
  Orange shading marks max(start, now − 60/90 days) through now in both graphs,
  not a future prediction or confidence band.
  Changing the level restarts the same-seed run and clears that run's scores,
  never the frozen calibration. No scenario/speed/manual-entry/error-sidebar UI.
  Task 054 uses existing consumption_30 = rate × 30 for the third headline,
  independent of balance, while additional-purchase math/exports stay unchanged.
  GUI launch/reset records the configured starting balance before rendering,
  enabling a labelled assumed-default estimate without inventing earlier readings.
  Empty-ledger/headless policies, zero/invalid states and the model are unchanged;
  all 23 focused checks and native GUI checks passed. Eight headless JSON/CSV
  reports match Task 053 byte-for-byte; this is not an accuracy improvement.
- Reveal hidden truth only through simulated now for plots/scoring, never fitting.
  Score new readings before refitting; freeze prior prediction/error snapshots.
  Compare with fixed 10 kWh/day and the current consumption/elapsed-time baseline
  on the same available records. Headless exports cover all three randomness
  levels. Report calendar month-end balance and matured
  30-day consumption errors, kWh MAE/bias and scored/pending counts by month and
  randomness level. Month-end means a pre-reading current-balance estimate at 00:00 UTC
  on the last calendar day, not a balance forecast issued one month earlier.
  Signed errors are prediction minus truth. Future horizons stay pending;
  yearly month-end results are not every-day accuracy. JSON/CSV/PNG outputs
  remain ignored research artefacts.

Acceptance: deterministic, explainable replay, reproducible calibration/data,
correct sparse/zero/invalid and 60/90-day boundaries, no future-data leakage,
slider reset/frozen-calibration behaviour and immutable pre-update errors within
a run. Task 053's 20 focused checks, headless exports and native GUI verification
passed. In its current stationary independent-noise examples, fixed 10 and the
all-history mean outperform the rolling line; the calibrated cold prior also
does not improve on fixed 10. Historical 052 results and current
exports do not close the broader 66.4 held-out
validation, adoption decision or 66.5 integration gate. Launch instructions,
equations and experiment limitations are in the research README.

### Ticket 66.4: Chronological Validation and Adoption Decision

Depends on: checked 66.1-66.3 outputs; fix evaluation rules before final scoring.

Outputs: repeatable chronological backtests, per-profile/cadence error tables and
plots, documented limits and a written go/no-go against the current baseline.

- At each cutoff use only observations and purchases known by that cutoff;
  separate tuning periods from later held-out periods. Truth is scoring-only.
- Report error in consumed/current kWh and additional 30-day purchase, plus
  remaining-days/run-out error where a finite comparison is meaningful. Include
  bias, worst cases and unavailable/fallback counts, not only an overall average.
- Compare future consumption directly, or define a no-future-purchase balance/
  run-out counterfactual from the cutoff. Unknown later purchases must not make
  a correct run-out prediction appear wrong; report horizons with no run-out.
- Check interval boundaries, UTC/local equivalence, rounding, mixed-meter
  isolation, corrections/deletions and all invalid/unavailable dataset cases.
- Agree numerical improvement/non-regression criteria before held-out scoring;
  show results by meter profile and reading cadence, not just favourable examples.

Acceptance: reproducible expected-output tests and held-out evidence justify a
go/no-go. No-go keeps the existing model; synthetic improvement alone does not
prove household accuracy. Record failures as small separately approved fixes.

### Ticket 66.5: Separately Approved Application Integration

Depends on: 66.4 evidence, an explicit go decision and fresh implementation approval.

Outputs: only if approved, a small reviewed integration/rollback plan and checks
for the dashboard and reminder callers through the same `run_forecast_model`.

Acceptance: preserve meter ownership, UTC/kWh contracts, actual-versus-estimated
labels, honest unavailable states and sparse-data fallbacks. No parallel model
inside the UI or email runner. Keep the current method recoverable; any cold-start
policy or output-contract change needs explicit separate scope and approval.

Shared reference: 450 kWh 30 days earlier, a 300 kWh purchase 15 days earlier
and 300 kWh now imply `(450 + 300 - 300) / 30 = 15 kWh/day`. At that instant:
300 kWh available, 20 days remaining, 450 kWh total 30-day use and only 150 kWh
additional purchase. Retain this distinction without adding a total-usage API field.
