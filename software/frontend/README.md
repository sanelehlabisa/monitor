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

Run checks from this directory with:

```powershell
npm test
npm run build
```

## Mobile flow

1. Enter email and verify the one-time code.
2. Create or select a meter/property by nickname.
3. Record a remaining balance in kWh or a top-up in kWh; date/time defaults to now.
4. Review the newest-first factual history and correct or delete entries.
5. Later, review clearly labeled estimates and configure email reminders.

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
types. History is combined newest-first while preserving clear labels.

Forecasting and the 30-day kWh recommendation remain later tickets. The selected
meter therefore keeps an honest `Not enough data` state even when factual
history exists. Estimates will recalculate from growing history only after the
reviewed deterministic domain work lands. This is simple math, not ML. Backend
persistence stays explicit raw SQL through Psycopg, with no SQLAlchemy.

Hardware status, OCR, anomaly, tariff and payment screens are not V1.
