# Frontend

React, Vite and Material UI application shell. The current screen honestly states
that authentication is inactive; product screens arrive through the active V1
tickets.

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
UI implementation. Roventics artwork can be selected only in an approved UI
ticket. Hardware status, OCR, anomaly, tariff and payment screens are not V1.
