# Task 017: Meter list and create UI

## Result

Signed-in users can now add a meter using only a nickname, see their accessible
meters, and select one in the mobile-first Material UI application.

## UI and API flow

- Added typed list/create/get meter calls through relative `/api` URLs with
  cookie credentials.
- Replaced the static placeholder with loading, failure, empty, create and
  populated states.
- Kept creation to one required 1-80 character name and provided a specific
  duplicate-name message.
- Added compact selectable cards and a back action without a router or new
  dependency.
- A selected meter clearly says `Not enough data` and explains that real balance
  and purchased-kWh history is required before estimates.
- Continued the Task 014 MUI theme, compact card layout and Roventics branding.

## Reuse

- Reused the session-aware app shell, relative API client, Material UI theme,
  signed-in card and existing server-rendered component/API test style.

## Verification

- Frontend tests: 8 passed across authentication, API contracts, empty, list and
  selected-meter states.
- TypeScript validation and the Vite production build passed; 902 modules were
  transformed.
- PostgreSQL, Mailpit, backend and frontend reported healthy.
- A live flow through the frontend proxy returned OTP request 202, verified a
  new user, created `Home`, listed it and retrieved it for selection.
- Synthetic Task 017 database rows were removed afterward: three OTP challenges
  and one user, with its meter/session removed by ownership cascades.
- `git diff --check` passed with only line-ending notices.
- `refocus.md` remained absent after the Task 015 workspace notice and was not
  recreated, modified or included.
