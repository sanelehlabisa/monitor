# Backend

FastAPI REST service with a reusable application factory, typed configuration
and a process-only health endpoint. Core settings use the `MONITOR_` prefix;
SMTP settings use the approved Job Talk-style names in `.env.example`.

## Code layout

```text
app/
  main.py          application factory; app.main:app stays the entrypoint
  settings.py      typed configuration
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

The backend connects directly through Psycopg. PostgreSQL's empty-volume init
runs `schema.sql` then `seed.sql`; Compose starts Uvicorn without running or
mounting numbered migrations. Integration checks no longer apply migrations.
Run checks only inside a dedicated verification environment with an explicitly
isolated `MONITOR_DATABASE_URL` and initialized schema, never the current DB:

```powershell
python -m pytest
```

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
10001. It defaults `MONITOR_ENVIRONMENT` to `production`, so the existing settings
validator refuses startup with the development OTP secret. Supply the unique
secret and deployment database/origin/SMTP values at runtime; no credential
is built into the image. Local `.env*` files are excluded from build context.

The image command does not install/upgrade SQL or create a database. Production
Compose and schema/upgrade orchestration require a separate Ticket 57 task. Process health
does not validate database/SMTP connectivity. Task 036's image builds and
disposable production smoke checks passed; see the software README.

## Authentication foundation

Ticket 43 implements the storage and backend policy used by human
authentication. Any normalized email can receive a challenge. Open signup
creates a user only after correct verification; repeated successful logins reuse
it. Fresh development seeds provision example accounts without credentials or
sessions: they still require ordinary email OTP verification to sign in.

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

## Current application access and forecasting

The owner-based access and opt-in reminders below remain the current application
contract. Task 059 derives administrator authority only from `users.type`, read
through existing OTP/session user queries on every authenticated request. Public
`is_admin` responses and opaque cookie shapes are unchanged; no email override,
environment fallback, cached cookie role or extra privilege query is used.
The guarded source upgrade and 68 isolated backend checks passed; final resource
cleanup is verified. Sharing remains 69.4 work; source app services remain off.

Task 015 implements raw-SQL storage for nickname-only meter profiles. The
repository supports owner-scoped CRUD plus explicit unrestricted lookups. Task
016 exposes authenticated `/api/meters` list/create and `/api/meters/{id}`
get/rename/delete routes. Regular users are always scoped to their own meters.
Users whose stored type is `admin` may list and manage every existing meter;
new meters still belong to the user who creates them.
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
remain owner-scoped; DB admins may manage every meter. Foreign, missing
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

Task 028 adds the finite command, now `python -m app.modules.reminder_runner`, for an
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
DB administrators may manage every meter; inaccessible and missing
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
the current volume unchanged; Task 059 now uses stored roles. Membership rows
still do not grant shared access. The approved source upgrade/one-time assignment
followed a new verified backup and isolated rehearsal before source execution.
[Frontend Tickets 69.5/69.6](../frontend/README.md) consume the resulting access
contract and fixed first-of-month planning date. The 30-day quantities and
predicted run-out remain distinct from that calendar planning date; no forecast
math or Ticket 66 adoption gate changes.
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
approval to stop only frontend/backend/Mailpit; they remain off, with the same
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
- Settle whole-meter deletion rights separately from leaving/removing members
  in the implementation prompt. Also settle creator/owner display and minimal
  sharing onboarding with 69.5; do not silently add invitations, unverified
  account creation or a second ownership authority.

Acceptance: two members can manage one meter while a non-member cannot reach
any of its protected resources, including nested IDs and search results.
Removal takes effect on the next request. Check DB-admin access, atomic
creation, sequential/concurrent last-member guards and account deletion without
accidental shared-data loss. Reuse existing APIs/error conventions where useful;
69.5 owns the minimal MUI integration.

### Ticket 69.7: Day-Before Planning Email to Meter Members

Depends on: 69.3/69.4's roles/memberships and 69.6's fixed planning date.

- Send the monthly planning email the day before the 1st, to every current
  member of that meter initially, with no per-member opt-in or schedule
  selector. This replaces the current owner-only, default-disabled monthly
  opt-in contract, not merely its recipient query. This is not every registered
  account. Global admin access alone does not make an admin a recipient; an
  admin receives only as a member.
- Choose the saved meter timezone, send time and scheduler/catch-up policy in
  the implementation prompt. Use that one explicit timezone for scheduling,
  not whichever member device happens to call the API. Keep UTC storage.
- Deduplicate monthly delivery per meter, recipient and target planning cycle:
  a December 31 send for January 1 belongs to the January cycle. Check month
  lengths, leap years and year boundaries; do not key it only by send month.
- Extend existing durable claims to recipient-level delivery for both reminder
  types. One recipient's failure/retry must not resend successful recipients;
  removal ends future eligibility, including rechecking membership before a
  pending send. Preserve abandoned-claim recovery and SMTP-failure release,
  without claiming exactly-once SMTP delivery across crashes.
- Retain predicted-low-balance reminders and their valid-forecast/lead-time
  eligibility, deduplicated per recipient and predicted local run-out date.
  Never send a low-balance forecast for unavailable/inconsistent history or
  invent one from defaults. A monthly email may instead request a fresh actual
  reading. Keep estimate labels and the warning to verify the physical meter;
  Monitor never buys electricity or guarantees a forecast.

Acceptance: use isolated SMTP capture to check multi-member fan-out, non-member
and admin-only exclusion, membership removal, recipient-specific retry/dedup,
overlapping runner claims, timezone/month/year boundaries and unavailable/zero/
valid low-balance cases. Reuse the finite runner and SMTP; no new service or
forecast implementation. Explain automatic member delivery in 69.5/69.6.

## Planned Ticket 70: Readable HTML Email and App Links

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
- The live app retains `not_enough_data` until its existing requirements are met.
  Optional cold-start defaults are labelled research scenarios, never actual
  meter readings or learned rates; live adoption requires separate approval.

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
