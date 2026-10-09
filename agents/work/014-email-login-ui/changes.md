# Task 014: Email login UI

## Result

Ticket 46 is complete. Monitor now has a working mobile-first Material UI
email/OTP flow with session restoration and logout. Authenticated users see an
honest `Your meters` empty state until Task 015 implements real profiles.

## UI and API flow

- Replaced the inactive shell with email and six-digit-code steps, resend and
  change-email actions, pending states and generic error feedback.
- Added a small typed API client for request, verification, `/api/me` restoration
  and logout; every call uses relative `/api` URLs and cookie credentials.
- Added a Vite development proxy to `backend:8000` without another environment
  variable or dependency.
- Prevented duplicate submissions while work is pending and limited the code
  field to phone-friendly numeric input.
- Kept authenticated output honest: normalized email, logout and a meter-list
  empty state with no fabricated balance or forecast.

## Visual reuse

- Reused the approved Switch direction: centered brand, pale background, compact
  white card, subtle shadow, full-width primary action and black/gold cues.
- Copied the approved circular Roventics robot from
  `../roventics/frontend/images/circular-logo.png` into Monitor as
  `frontend/public/roventics-logo.png`; the sibling repository was not modified.
- Kept the implementation native to Material UI and added no UI/state/router or
  testing package.
- Implementation exceeds the 100-line aim because session restoration, two form
  steps and signed-in state form one usable authentication flow; API calls remain
  isolated in a small client.

## Product direction recorded

- Clarified that active V1 "devices" are nickname-only software meter profiles,
  not hardware credentials.
- Recorded the future meter-selection flow: balance and purchased-kWh entries,
  history, remaining balance/days and a 30-day recommendation.
- Recorded one shared deterministic forecast method that recalculates per meter
  as history grows. This is not ML or reinforcement learning, and cold starts
  remain `Not enough data`.
- Reaffirmed explicit raw SQL/Psycopg and no SQLAlchemy for future backend work.

## Verification

- Frontend tests: 6 passed across rendered UI states and API request contracts.
- TypeScript checking and the Vite production build passed; 901 modules were
  transformed and the production bundle was generated.
- PostgreSQL, Mailpit, backend and frontend all reported healthy.
- A live flow through `http://127.0.0.1:5173/api` returned request 202, verified
  the Mailpit code, restored the same user through `/api/me`, logged out with 204
  and then returned 401. The local logo returned HTTP 200.
- Headless Edge screenshots at compact and desktop widths showed the branded
  login card after session restoration completed.
- `docker compose config --quiet` and `git diff --check` passed.
- Live-flow cleanup left zero Task 014 sessions, users and OTP challenges.
- Temporary containers and their network were removed after verification; the
  PostgreSQL and frontend dependency volumes were preserved.
- `refocus.md` retained SHA-256
  `8EE807DBC69F88F225D93D608DA7A5537FF2745454109F659342521B90849257`,
  remained untracked and was excluded from the commit.
