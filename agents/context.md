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
means recording electricity already bought. Email reminders may later prompt a
monthly purchase or warn about a predicted low balance.

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

Development runs PostgreSQL, backend and frontend through
`software/dev.docker-compose.yaml`. No production/cloud infrastructure should be
added without an approved ticket.

## Authentication

Tasks 005-006 are historical records of the superseded Keycloak baseline. Task
007 removed that integration. Planned human authentication uses authorised
email addresses, short-lived hashed one-time codes and secure HTTP-only cookie
sessions. Generic request responses must avoid email enumeration.

Device UUIDs, device credentials and provisioning are not V1 requirements.
They remain future research if automated meter capture is later justified.

## Work history and current direction

- Tasks 001-004 created the repository, three-service Docker stack, FastAPI
  baseline and direct-Psycopg migration system.
- Tasks 005-006 implemented the now-superseded Keycloak path.
- Task 007 removed Keycloak and retained the Material UI foundation.
- Task 008 changes active planning from camera/OCR collection to manual kWh
  entries, forecasts and reminders. It does not implement those features.

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
