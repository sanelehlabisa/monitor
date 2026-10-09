# Frontend

React, Vite and Material UI application with a working passwordless email login
and meter picker. It restores cookie sessions through `/api/me`, supports
email/code/resend/logout, and lets a signed-in user add, list and select
nickname-only software meters.

Run checks from this directory with:

```powershell
npm test
npm run build
```

## Planned mobile flow

1. Enter email and verify the one-time code.
2. Create or select a meter/property by nickname.
3. Record a remaining balance in kWh or a top-up in kWh; date/time defaults to now.
4. Review actual history and clearly labeled estimates.
5. Configure monthly and optional predicted low-balance email reminders.

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
cookie-authenticated API. Creation asks only for a name, and selecting a meter
currently shows an honest `Not enough data` state. Balance and purchased-kWh
history, deterministic estimates and the 30-day kWh recommendation arrive in
later tickets. Estimates will recalculate from growing history and remain
`Not enough data` until real entries support them. This is simple math, not ML.
Backend persistence stays explicit raw SQL through Psycopg, with no SQLAlchemy.

Hardware status, OCR, anomaly, tariff and payment screens are not V1.
