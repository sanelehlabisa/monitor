# Repository Context

Monitor is a software-only prepaid-electricity planner: email login -> named
meters -> manual balance/top-up kWh records -> transparent estimates.
The root [README](../README.md) owns stable roadmap IDs and priority. Component
READMEs hold details; historical results stay in work/ and Git.

## Current contracts

- FastAPI uses explicit Psycopg SQL, not an ORM. React/Vite/Material UI is the
  mobile-friendly frontend. Development uses software/dev.docker-compose.yaml
  and ignored software/.env. Never print/commit secrets or private records.
- A meter needs only a name. Users manage their own meters; DB admins may manage
  every meter. Membership storage exists, but shared access/last-member guards
  remain future 69.4/69.5 work.
- Record actual remaining kWh (non-negative) and purchased kWh (positive), with
  editable occurrence times separate from audit times. Store UTC instants;
  the browser converts local input/display.
- Open OTP signup creates a regular user only after verification. Returning login
  preserves users.type; that constrained user/admin column is the sole authority,
  read each request. No env/email override or cookie-cached role. Preserve opaque
  HTTP-only cookies, digest-only OTP/session storage and abuse controls.
- Fresh-only seeds provision hlabisasanele730@gmail.com as admin and fictional
  examples, without credentials/sessions. Later role changes are manual DB
  operations, never startup or login re-promotion.
- The UI has an open white layout, blue/teal Monitor branding, compact system
  typography, stacked logo/name, Back and email/red icon-labelled Sign out.
  /meters lists profiles; /meters/<uuid> supports direct login/reload/history.
  / and /meters/ remain compatible entries; login is not a separate URL.
- Estimates lead; record forms/history open on demand. Search is server-side by
  name/owner email, shown above 10 unfiltered meters or for an active query.
  Preserve request-version guards, form resets and unavailable/error recovery.

## Forecast boundary

All callers use one run_forecast_model function with that meter's history:

    consumed = previous_balance + intervening_top_ups - current_balance
    daily_usage = consumed / elapsed_days

Require at least two actual readings with positive elapsed time. Include top-ups
and surface impossible negative consumption/inconsistent chronology. Show
Not enough data/Inconsistent history instead of inventing numbers. Genuine
zero use has no finite run-out date.

The deterministic time-weighted rate produces estimated current balance,
remaining days/run-out and additional kWh for the next 30 days:
max(0, daily_usage * 30 - estimated_balance). This is not total monthly usage or
Rand cost. Keep latest actual reading/time and calculation time visible.
Recalculate after ledger changes/Refresh; never silently adopt a research prior.

## Database and runtime safety

- database/ keeps only schema.sql, seed.sql and README.md. PostgreSQL runs SQL
  only on an empty volume. Startup never upgrades SQL or replays seeds. Agree
  an explicit safe repair for partial initialization; never reset automatically.
- Task 059 upgraded the existing DB after verified backup/isolated rehearsal,
  promoting only the approved existing admin. Preserve nine domain tables and
  BOTH monitor.schema_migrations and public.schema_migrations history tables.
- Task 060 retires inactive SQL/runner sources, not stored history. The database
  README records recoverable SQL/backups. Preserve pending work, backups,
  research archives, refocus.md and historical work records.
- At Task 060 preflight, monitor-dev-database-1 was healthy/running on
  monitor-dev_postgres-data; backend/frontend/Mailpit remained stopped as agreed.
  Recheck actual state before work. Tasks 060-062 do not authorize source starts.
- Run checks against isolated labelled DB/Mailpit resources, never source data
  or real email. The finite reminder CLI can send mail even with --help; verify
  by import/isolated checks only.
- Live browser login/end-to-end verification after 059 is outstanding. Isolated
  HTTP checks are not live-user or household validation.

## Current source layout (Tasks 060-062)

060 retired old setup/stale active context. Backend logic lives under
app/modules, Pydantic validation under schemas and routers under endpoints;
main/settings/database and version-bearing __init__ stay at app root.
Frontend login/meters screens live under routes, meter-only components under
routes/meters, shared navigation under components and helpers under lib.
Keep behavior, URLs, validation and permissions unchanged; add no dependency,
framework/layer, compatibility shim or eager re-export architecture.
All 67 backend and 33 frontend checks passed; OpenAPI is byte-identical and
TypeScript/Vite plus mocked browser checks passed using pinned Docker deps.
The host node_modules has missing MUI declarations and was left unchanged.
Source services remain stopped; only isolated verification resources were used
and cleaned. Details/recovery are in the work records. The user authorized the
Git handoff of completed Tasks 059-062 to master; earlier no-commit notes describe
their completion-time state. The next implementation still needs prompt approval.

## Remaining priorities

1. Next is 69.4 backend shared-access guards, then 69.5 minimal sharing UI.
   Repeat owner-membership backfill at cutover; first
   settle creator-delete cascades, whole-meter deletion and concurrent last-member
   safety. Membership rows alone do not activate sharing.
2. 69.6 fixes planning to the 1st, separate from predicted run-out and retaining
   current rolling 30-day quantities/model. It is not active yet.
3. 69.7 emails all meter members (not all accounts/admins) the day before the 1st.
   Preserve low-balance eligibility, saved-local calendar/UTC storage and
   per-recipient dedupe/removal behavior. Current reminders remain owner-only,
   opt-in, default off, with settings hidden in UI. Reuse the finite runner/SMTP.
4. HTML email 70 (plain fallback/trusted app links), usability 65, offline forecast
   validation 66, deployment 57, then household/external evidence 56/67.
   Each implementation needs its own questions, prompt and approval.
5. Future mobile/local-only 68 may provide guest device storage and optional
   account login; it does not weaken today's authenticated backend.

## Deferred research

Tariffs/Rand/cost forecasts, payments, hardware, camera/OCR, MQTT, device ingestion
and ML are not V1. Preserve research and non-invasive safety rules; anomalies are
never proof of theft. Read-only Switch UI/Roventics brand inspection is allowed;
never modify sibling repositories without separate authorization.

Offline forecasting research has its own dependencies/environment under backend.
simulator.py is the sole entrypoint: 730-day synthetic replay, nominal 0.1 sec/day,
moving orange 60/90-day context, two plots and a randomness slider. The forecast
horizon remains 30 days. Its calibrated prior/rolling line is NOT integrated.
Retain 66.1/66.2 acceptance, 66.3 review, chronological 66.4 go/no-go and fresh
66.5 approval. Current independent-noise evidence favors baselines, not adoption.
Preserve ignored .tmp/task053/legacy-research.zip and
.tmp/task055/simulator_checks.py: they contain unique retired research sources.
