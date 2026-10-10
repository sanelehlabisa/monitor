# Frontend

React, Vite and Material UI application with passwordless email login, meter
management and manual kWh history. It restores cookie sessions through
`/api/me`, supports email/code/resend/logout, and lets a signed-in user add,
list, select, rename and delete nickname-only software meters.

Regular users see and manage only their own meters. Users whose normalized email
is configured as an administrator see an Admin indicator, every meter's owner
email, and the same select/rename/confirmed-delete controls for all meters. New
meter creation remains intentionally name-only and always belongs to the signed-
in user.

Administrators default to a `My meters` view so they can quickly create and test
profiles owned by their admin account. `All meters` shows every system profile
with owner labels and the same full management controls. Switching views changes
only presentation; it does not change ownership or backend access policy.

The meter list has an explicit Search/Clear form backed by
`GET /api/meters?q=...`. Regular users search only their accessible profiles;
administrators may find system profiles by meter name or owner email. The
frontend renders the server response and does not duplicate keyword filtering.

Development uses polling to watch bind-mounted sources because Docker Desktop
can miss native file-change events. When dependencies change, refresh the named
frontend dependency volume and restart the frontend as described in the software
README; rebuilding an image alone does not update an existing dependency volume.

Run checks from this directory with:

```powershell
npm test
npm run build
```

## Docker targets

`development` retains Vite on port 5173 and bind-mount reload. The default
`production` target builds with the existing npm lockfile and copies only `dist/`
into `nginx:1.30.5-alpine3.24`; Node/npm and application source are not copied into
the serving stage. Local `.env*` files are excluded from the build context.

Nginx listens on port 80. It forwards `/api` and `/api/...` to `backend:8000`
without stripping the API path, while other application routes fall back to
`index.html`. Missing `/assets/...` files return 404 rather than SPA HTML. A
backend network alias/service must exist before Nginx starts. HTTPS/public proxy
configuration is deferred; production cookie login requires HTTPS. Build
commands and completed image verification are recorded in the software README.

## Mobile flow

1. Enter email and verify the one-time code.
2. Create or select a meter/property by nickname.
3. Review the prominent planning estimate and its latest factual reading.
4. Use the Balance records or Top-up records tab to add, correct or delete an
   entry; date/time defaults to the browser's local time.
5. Use Refresh to request current estimates without adding a record or reopening
   the meter. Estimates are a snapshot at the displayed local calculation time.

The primary entry actions must take only a few seconds on a phone. Do not require
a municipal meter number, tariff, Rand amount, image or device setup. Show the
last actual reading time beside estimated balance, daily usage, remaining days,
likely next-top-up date and 30-day recommended kWh.

Use "Not enough data" when the backend cannot support a forecast. Make correction
and deletion behavior explicit; never hide inconsistent history behind a smooth
chart.

Future UI may take inspiration from the sibling Switch dashboard's compact cards,
clear primary actions and mobile sizing, but Monitor stays a native React/Material
UI implementation. Task 014 uses those principles and a local copy of the
approved circular Roventics robot logo. Development browser requests use relative
`/api` URLs through Vite's proxy to the backend; cookies never enter browser
storage or page text.

The signed-in home loads real nickname-only software meter profiles from the
cookie-authenticated API. Creation asks only for a name. Selecting a meter loads
its actual balances and purchased top-ups, shows the latest factual balance,
and provides compact create/edit/confirmed-delete controls for both record
types. Each tab shows its own newest-first factual history.

The selected meter dashboard shows latest actual balance separately from the
estimated current balance, daily use, remaining days, run-out date and 30-day
kWh recommendation. It reloads the backend dashboard after every ledger change.
Task 035 adds an icon-labelled Refresh action above the planning summary. It
uses the same dashboard loader as meter opening and successful ledger changes;
there is no automatic polling. Refresh is disabled while loading or saving.
Failed reads hide estimates and show `Estimates unavailable` with retry guidance,
not a permanent spinner. Already-loaded records remain available after failure.
If a write succeeded, its form clears and the message confirms it was saved:
Refresh retries only the read, never the purchase or balance write. Responses
from a meter left, reopened or signed out of cannot overwrite the newer view.

Insufficient or inconsistent history shows an explicit state without invented
numbers; valid zero use has no fake run-out date. The browser does not calculate
forecasts. Backend persistence stays explicit raw SQL through Psycopg, with no
SQLAlchemy, and the replaceable first forecast model is simple math rather than
ML.

Balance and top-up histories are separated into matching tabs so the selected
record type owns both its entry form and its newest-first factual list. Datetime
inputs are interpreted in the calling browser's timezone, converted to UTC for
the API/database and rendered locally when returned.

Task 033 removes reminder settings from the frontend to keep the PoC focused.
The backend API and finite runner remain available for existing opt-ins. New
settings still default off, with the existing hardcoded monthly day 1 and
predicted-low-balance lead time of 3 days; the browser makes no reminder calls.

Hardware status, OCR, anomaly, tariff and payment screens are not V1.

## Repeatable local demo

Use a separate test email and a new meter named `Demo Home`. Get the sign-in code
from local Mailpit at `http://localhost:8025`. Dates below are relative to now;
use the same local clock time for all three records.

| Tab | Record time | kWh |
| --- | --- | --- |
| Balance records | Eleven days ago | 100 |
| Top-up records | Six days ago | 20 |
| Balance records | Yesterday | 80 |

The interval used 40 kWh over ten days: `(100 + 20 - 80) / 10 = 4 kWh/day`.
The planning card should show approximately 76 kWh now, 19 days remaining,
a run-out/top-up-by date 19 days from now and 44 kWh needed for the next 30 days.
The latest actual reading stays 80 kWh at yesterday's observation time. Small
differences are expected as time passes; the 44 kWh recommendation accounts for
the estimated 76 kWh already available.

1. Edit yesterday's balance to 70 kWh. The usage rate should refresh to 5 kWh/day
   without reopening the meter. Restore it to 80 afterward.
2. Edit the top-up to 30 kWh; the rate should become 5 kWh/day. Restore 20 kWh.
3. Delete yesterday's balance and confirm the prompt. One remaining reading
   should show `Not enough data`; add yesterday's 80 kWh reading again.
4. Select Refresh to update the calculation time without creating records.
   Reopen the meter or reload the page; records and the session should persist.
5. In another browser profile, sign in with a second test email. The first
   user's meter must be absent. A configured admin can instead select `All
   meters`, search by the owner's email and manage that meter.
6. Delete only the demo meter when finished and sign out.

Input times use the browser's local timezone; the API and database retain the
equivalent UTC instants. This walkthrough verifies the technical flow. A real
household trial is still needed to establish whether manual entry is convenient.
