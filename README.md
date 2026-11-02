# Monitor

Plan prepaid electricity use with simple kWh calculations. Record balances and
top-ups to estimate current balance, days remaining, run-out and monthly needs.

The deployed app currently uses email login. Next: local browser use without
an account, with optional login for account storage and access from another
device. Guests use local storage; signed-in users use the backend. The homepage
will offer Use without logging in. Log in and save to account will save the
existing guest meter/history after email verification, then hide the guest prompt.
Local saving cannot guarantee recovery after browser data is cleared.

## Development

React, Material UI, FastAPI, PostgreSQL and direct SQL.
[Software setup](software/README.md): two Compose files, one `.env`.
[Deployment](software/nginx/README.md): production operations.

## Next: easier onboarding

| Order | Ticket | Title |
| --- | --- | --- |
| 1 | 68.1 | Guest flow design |
| 2 | 68.2 | Local forecast calculation |
| 3 | 68.3 | Local records and workspace |
| 4 | 68.4 | Login and storage routing |
| 5 | 68.6 | Three-day remembered login |
| 6 | 65 | Phone and desktop usability |
| 7 | 57.3 | Deploy guest onboarding |
| 8 | 67.1 | Reddit beta recruitment |
| 9 | 67.2 | One-month feedback review |

Details: [frontend](software/frontend/README.md#ticket-68-guest-web-onboarding)
and [release plan](software/README.md#planned-validation-and-release).
Preserve current email accounts, sharing and admin access.

## Parallel and later

- **56 — Personal validation:** compare real entries with saved estimates.
- **70 — Reminder emails:** login HTML is complete; reminder HTML remains.
- **66.1–66.5 — Forecast research:** datasets, plots, simulator, evaluation,
  then integration only if justified. [Research](software/backend/research/forecasting/README.md).
- **68.5 — Mobile installation:** revisit after beta feedback.
- Hardware/OCR/ML, Rand/tariff forecasts and payment execution remain deferred.

## Current behavior

One actual balance uses a labelled 10 kWh/day assumption. Valid later readings
supply that meter's measured use; inconsistent history does not fall back
silently. Planning targets the next UTC 1st and the actual month's length.
Purchases/balances are kWh; no meter serial number is needed.

## Repository

- [Backend](software/backend/README.md), [frontend](software/frontend/README.md)
  and [database](software/database/README.md).
- [Deferred hardware](hardware/README.md) and [OCR](software/ocr/README.md).
- [Agent instructions](AGENTS.md) and
  [historical ticket register](agents/work/090-independent-guidance/prior-guidance.md).

Existing ticket IDs/work records are retained. Open tickets do not authorize
implementation. Proprietary — Roventics Pty Ltd.
