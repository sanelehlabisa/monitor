# Task 034: Live demo flow check

## Results

- Completed the approved live walkthrough using isolated headless Edge contexts,
  the real Vite proxy/API, PostgreSQL and Mailpit. No testing dependency was added.
- Found a development blocker: Docker had current source files, but Vite served
  cached pre-Task-033 modules because native bind-mount file events were missed.
  Its existing dependency volume also lacked the approved MUI icon package.
- Enabled Vite polling with a two-line configuration change. Refreshed only the
  frontend dependency volume from the existing lockfile and restarted Vite.
  Documented dependency refresh/restart and a repeatable demo in the READMEs.
- The example produced 4.000000 kWh/day, 75.997 kWh estimated balance, 19.00
  days remaining and 44.003 kWh recommended for 30 days. The tiny difference
  from 76/44 kWh is elapsed time after the reference minute.
- Technical validation is complete. Ticket 56 stays open for real household
  usability evidence; deployment and the future logo remain separate work.

## Reuse

- Used existing OTP/cookie authentication, scoped meter/ledger APIs and the
  single run_forecast_model boundary without changing those implementations.
- Used Mailpit's captured OTPs for two synthetic users. For admin checks, created
  one temporary session for an existing configured administrator; no admin
  configuration, identity or existing household records were changed.
- Kept the temporary browser driver and screenshots under ignored .tmp/ rather
  than introducing a permanent testing framework or committing credentials.

## Verification

- PASS: 16 grouped browser/API checks plus exact fixture cleanup: real email
  login and HTTP-only cookie; name-only meter creation; both ledger tabs;
  expected forecast arithmetic; corrections/deletions and immediate refresh;
  inconsistent/insufficient/zero-use states; session restoration on reload;
  ordinary-user isolation; server search/clear; admin My meters/All meters,
  owner-email search and another user's meter rename; duplicate/future-time
  validation; no reminder requests; and sign-out returning HTTP 401.
- PASS: browser timezone set to Africa/Johannesburg; local input, returned UTC
  timestamps and raw-SQL PostgreSQL instants represented the same observation.
- PASS: screenshots inspected at 1200px desktop and 390px phone widths; neither
  had horizontal overflow. Latest actual readings remained distinct from estimates.
- PASS: zero uncaught browser errors in the completed walkthrough.
- PASS: docker compose exec frontend npm run build (TypeScript and Vite).
- PASS: Vite log reports hmr update /src/App.tsx after a timestamp-only source
  change; current modules serve the Task 033 layout without the reminder panel.
- PASS: only this task's synthetic users, cascading meters/records/sessions,
  OTP rows, temporary admin session and captured Mailpit messages were removed.
  Cleanup confirmed zero remaining fixture users and OTP challenges; existing
  records and captured emails were preserved.
- PASS: git diff --check. The implementation change is limited to two Vite
  configuration lines; no backend, database, dependency or forecast change.
