# Task 033: Dashboard UI cleanup

## Results

- Widened the authenticated workspace from the narrow login width to a
  responsive medium container while retaining the compact login card.
- Moved the selected meter name and owner email into one top header for every
  user, not only administrators.
- Reworked the available forecast into a prominent planning card containing
  estimated balance, remaining days, top-up-by date and recommended 30-day kWh.
  The latest actual balance and local observation time remain visibly separate.
- Replaced the combined ledger with accessible Balance records and Top-up
  records tabs. Each tab owns its matching entry form and newest-first history.
- Added text-labelled Material UI icons to authentication, navigation, meter,
  search and ledger actions using `@mui/icons-material` 9.4.0.
- Centralized browser-local input/display and UTC API conversion helpers. No
  database, API timestamp contract or forecasting calculation changed.
- Removed the reminder panel, state and API client calls from the frontend.
  Backend settings, endpoints, finite runner, existing opt-ins and disabled
  defaults remain unchanged; monthly day 1 and lead time 3 days stay hardcoded.
- Logged future Ticket 58 for a user-supplied Monitor-specific logo and modest
  Roventics acknowledgement. No branding asset changed in this task.
- Updated the root roadmap, repository context, software overview and frontend
  usage notes. Recorded the coordinated UI review-size exception in the prompt.

## Reuse

- Reused the selected-meter and dashboard refresh flow in `App.tsx`.
- Reused the existing backend forecast response and honest unavailable and
  inconsistent states; no browser forecast logic was introduced.
- Reused the existing ledger create/update/delete callbacks and confirmation
  flow inside the new tabs.
- Reused the backend reminder constants and delivery behavior without edits.

## Checks

- PASS: `npm.cmd test -- --reporter=verbose --maxWorkers=1` — 20 tests passed
  across 3 files, including forecast hierarchy, record tabs and date helpers.
- PASS: `npm.cmd run build` — TypeScript check and Vite production build.
- PASS: source search found no reminder UI text, settings type or reminder API
  call under `software/frontend/src`.
- PASS: `git diff --quiet -- software/backend software/database` — backend and
  database are unchanged.
- PASS: reminder source still defines day 1, lead time 3.00 and both defaults
  disabled.
- PASS: `git diff --check` (line-ending conversion warnings only).
