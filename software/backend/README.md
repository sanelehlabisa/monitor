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
