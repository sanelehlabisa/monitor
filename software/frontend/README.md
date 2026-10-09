# Frontend

React, Vite and Material UI application with a working passwordless email login.
It restores cookie sessions through `/api/me`, supports email/code/resend/logout
and shows an honest meter-list empty state after authentication.

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

The signed-in home will list nickname-only software meter profiles in Ticket 49.
Selecting a meter will eventually open its remaining-balance and purchased-kWh
history, deterministic estimates and 30-day kWh recommendation. Estimates are
recalculated from that meter's growing history and remain `Not enough data` until
real entries support them. This is simple math, not ML. Backend persistence stays
explicit raw SQL through Psycopg, with no SQLAlchemy.

Hardware status, OCR, anomaly, tariff and payment screens are not V1.
