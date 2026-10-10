# Repository Context

Roventics Monitor is a free, software-only electricity planning application for
prepaid households. It helps users understand how much electricity to add and
when through manual kWh records and simple, transparent forecasts.

## Active V1

A user authenticates by email OTP, creates one or more named meter/property
profiles, and records two kinds of events:

- actual remaining balance in kWh at an observed date/time; and
- manually purchased top-up energy in kWh at a purchase date/time.

Dates default to now but remain editable. A municipal meter identifier is not
required. Each meter belongs to its user in V1, and every API/query must enforce
that ownership. Sharing and multi-user meter access require later evidence.

V1 does not accept Rand amounts, use tariffs or execute purchases. "Top-up"
means recording electricity already bought. Users may opt into monthly planning
email or a predicted-low-balance email when a valid forecast exists.

## Forecast contract

Between two valid actual balance readings:

```text
consumption_kwh = previous_balance_kwh
                  + top_ups_kwh_during_period
                  - current_balance_kwh

daily_usage_kwh = consumption_kwh / elapsed_days
```

Use deterministic calculations and show their assumptions. At least two actual
balance readings with positive elapsed time are required before calculating a
usage rate. Account for top-ups inside the interval. Reject or clearly surface
impossible negative consumption, duplicate/reordered times and inconsistent
entries. Never turn insufficient data into a confident prediction.

Estimated current balance, remaining days, likely run-out/next-top-up date and
a 30-day kWh recommendation must be labeled as estimates. Always show the latest
actual reading and its observation time beside forecast output.

## Active technology

- `software/backend/`: FastAPI REST service and pure forecasting/domain logic.
- `software/database/`: PostgreSQL with explicit versioned SQL through Psycopg;
  no ORM.
- `software/frontend/`: React, Vite and Material UI, designed mobile-first.
- `software/ocr/`: deferred research only, not an active dependency.
- `hardware/`: deferred research only, not an active V1 dependency.

Development runs PostgreSQL, Mailpit, backend and frontend through
`software/dev.docker-compose.yaml`. No production/cloud infrastructure should be
added without an approved ticket.

## Authentication

Tasks 005-006 are historical records of the superseded Keycloak baseline. Task
007 removed that integration. Task 010 allows open email signup and implements
normalized user/OTP storage plus HMAC-only challenge policy. Task 011 delivers
those codes through an SMTP abstraction and isolated Mailpit development
capture. Task 012 adds digest-only, fixed 30-day session storage and policy. A
user is created only after successful verification. Task 013 exposes the human
authentication routes and transports opaque sessions in secure HTTP-only
cookies. Generic request responses avoid account enumeration, and neither email
nor an OTP is an API token.

Device UUIDs, device credentials and provisioning are not V1 requirements.
They remain future research if automated meter capture is later justified.

## Work history and current direction

- Tasks 001-004 created the repository, three-service Docker stack, FastAPI
  baseline and direct-Psycopg migration system.
- Tasks 005-006 implemented the now-superseded Keycloak path.
- Task 007 removed Keycloak and retained the Material UI foundation.
- Task 008 changes active planning from camera/OCR collection to manual kWh
  entries, forecasts and reminders. It does not implement those features.
- Task 009 aligns the inactive Material UI shell with that product direction.
- Task 010 adds open-signup user/OTP storage and policy without HTTP or delivery.
- Task 011 adds SMTP OTP delivery and Mailpit capture without an HTTP surface.
- Task 012 adds opaque multi-device session storage and policy without HTTP.
- Task 013 completes the human auth API and HTTP-only cookie transport.
- Task 014 adds the session-aware Material UI login flow and branded meter-list
  empty state.
- Task 015 adds raw-SQL nickname-only meter persistence and owner-scoped CRUD.
- Task 016 exposes authenticated meter CRUD. Regular users are owner-scoped;
  emails configured in `MONITOR_ADMIN_EMAILS` may manage all existing meters.
- Task 017 connects the Material UI home to real meter list/create/select APIs
  and keeps a newly selected meter at `Not enough data` until ledger work lands.
- Task 018 completes Ticket 49 with rename/delete controls and an administrator
  view that identifies owners and manages all meters. Regular-user isolation is
  unchanged.
- Task 019 adds raw-SQL actual balance observations with non-negative three-
  decimal kWh, unique per-meter occurrence times and scoped correction/deletion.
- Task 020 adds raw-SQL purchased top-up events with positive three-decimal kWh,
  repeated occurrence times and the same scoped correction/deletion behavior.
- Task 021 exposes nested authenticated balance/top-up CRUD, rejects future or
  timezone-naive events and applies the established user/admin meter scope.
- Task 022 completes the balance/top-up delivery with mobile-first Material UI
  entry, correction, deletion, latest-actual and combined-history states.
- Tasks 023-024 complete Ticket 52 behind one replaceable
  `run_forecast_model` function. Its first implementation is deterministic,
  time-weighted math with explicit unavailable states and no hidden buffer.
- Task 025 exposes a freshly calculated, authorised meter dashboard containing
  latest actual data, separate ledgers, combined factual history and forecasts.
- Task 026 completes Ticket 54 with responsive Material UI estimate cards and
  automatic dashboard refresh after every successful ledger change.
- Task 027 adds opt-in raw-SQL reminder preferences per meter, including monthly
  day, predicted-low-balance lead days and browser-supplied IANA timezone.
- Task 028 adds durable reminder delivery claims and a finite runner that sends
  owner-only monthly/low-balance email through the existing SMTP boundary.
- Task 029 exposes authenticated owner/admin reminder preference reads and saves
  without exposing or triggering the delivery runner.
- Task 030 adds per-meter Material UI reminder controls with disabled defaults,
  browser timezone capture and clear forecast limitations.
- Task 031 separates the administrator workspace into `My meters` and `All
  meters`, keeping admin-created profiles owned by the admin while retaining
  full management access to every user's profile.
- Task 032 adds owner-scoped raw-SQL meter keyword search by profile name or
  owner email and a minimal frontend Search/Clear form that consumes it.
- Task 033 widens and reorganizes the selected-meter UI around a prominent
  planning summary, a meter/owner header and separate balance/top-up tabs. It
  removes reminder configuration and requests from the frontend while leaving
  the reminder backend, disabled defaults and existing opt-ins unchanged.
- Task 034 verifies the live browser sign-in, meter/ledger/forecast flow, UTC/local
  timestamps, user isolation and admin access. It enables Vite polling after
  finding stale Docker-served modules, refreshes the existing frontend dependency
  volume and documents a repeatable local demo. Technical checks passed; Ticket
  56 remains open for real household usability feedback before deployment.
- Task 035 completes Ticket 59 with an icon-labelled manual Refresh action and
  one shared dashboard loader. Failed initial/manual/post-save reads withhold
  estimates, retain available records and provide retry guidance. Reads never
  repeat saved writes; navigation/sign-out invalidate older dashboard responses.
  No automatic refresh, dependency, backend or forecast-model change was added.

Household validation and deployment remain later steps, and the Monitor logo
still awaits the user-supplied asset.

After login, the active product flow is a list of the user's nickname-only
software meter profiles. Selecting one meter provides balance and purchased-kWh
entry actions, factual history, estimated current balance/days/run-out, and a
30-day kWh purchase recommendation. The UI shows `Not enough data` or
`Inconsistent history` rather than fabricating unavailable estimates.

Forecasting uses one reviewed deterministic method for every meter and
recalculates from that meter's history whenever a new point is added. All callers
use the single replaceable model function so a later evidence-backed method does
not require API/UI rewrites. History improves the estimate incrementally, but
this is not reinforcement learning or ML. A new meter has no guessed usage
baseline and must show `Not enough data` until real readings support the
calculation.

Development Compose reads its explicit values from the ignored `software/.env`.
The committed `.env.example` contains only safe local examples; personal admin
emails and secrets must remain untracked.

The root README owns stable ticket IDs and the current execution order. Ticket
48 performs an explicit active-code/domain cleanup before authentication and
feature tickets proceed.

## Deferred research

Hardware, firmware, camera capture, OCR, device upload, MQTT, anomaly ML and
meter interfaces are preserved but deferred. Revisit automation only if real
users find manual entry too inconvenient. Desktop OCR tests are never hardware
validation, and uncertain OCR must never become a trusted balance silently.

Automated top-ups, payment integration, tariffs, Rand forecasts, SMS, push
notifications, municipal dashboards and postpaid billing are also deferred.
Any future payment path requires authorised providers, consent, auditability and
explicit failure handling.

Any future physical meter work must remain external and non-invasive. Never
open, electrically modify, bypass or interfere with an installed meter.
Anomalies are investigation signals, not proof of theft or tampering.

## UI and brand references

The user has authorised read-only inspection of `../switch/hardware/web/` for
mobile interaction inspiration and `../roventics/frontend/images/` or
`../switch/assets/branding/roventics/` for future company artwork. Monitor UI
must remain a native React/Material UI implementation. Never modify sibling
repositories without a separate explicit request.

## Documentation rules

Use the nearest README; do not create a `docs/` directory. Keep root roadmap
summaries short and detailed requirements in component READMEs. Work records use
sequential three-digit directories. Do not commit secrets, private bills,
customer data, meter photographs or local database contents.
