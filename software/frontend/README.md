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

Run checks from this directory with:

```powershell
npm test
npm run build
```

## Mobile flow

1. Enter email and verify the one-time code.
2. Create or select a meter/property by nickname.
3. Review the prominent planning estimate and its latest factual reading.
4. Use the Balance records or Top-up records tab to add, correct or delete an
   entry; date/time defaults to the browser's local time.

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
