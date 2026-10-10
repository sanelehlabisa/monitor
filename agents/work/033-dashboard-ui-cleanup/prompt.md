# Task 033: Dashboard UI cleanup

## Aim

Make the selected-meter workspace demo-ready by putting the meter identity and
essential electricity-planning estimates first, while keeping balance and
top-up management compact and easy to distinguish.

## Clarifications

- Question: What information should dominate the selected-meter screen? Answer:
  Put a clear planning summary near the top showing estimated current balance,
  estimated run-out/top-up-by date, estimated remaining days and recommended
  30-day top-up kWh. Keep estimates explicitly labelled and retain honest `Not
  enough data` or `Inconsistent history` states.
- Question: Where should the selected meter identity appear? Answer: Show the
  meter name at the top beside its owner email.
- Question: How should manual records be managed? Answer: Put balance records
  and top-up records lower on the page behind a tab-style control, with the
  selected tab exposing the relevant entry and record-management experience.
- Question: What visual cleanup is approved? Answer: Widen the responsive main
  card so desktop text does not wrap unnecessarily, and add clear icons beside
  button labels using the official `@mui/icons-material` package at the version
  matching the installed Material UI packages.
- Question: What happens to reminder controls? Answer: Remove the whole email
  reminder section and its frontend requests from the selected-meter UI. Keep
  the backend settings, API and runner intact. Existing opt-ins continue to
  work; new defaults remain disabled. Retain the existing hardcoded monthly day
  1 and predicted-low-balance lead time of 3 days.
- Question: How should dates and times behave? Answer: PostgreSQL and API values
  remain timezone-aware UTC. Datetime inputs and displayed history/forecast
  dates use the calling browser's local timezone, including the existing
  `toISOString()` conversion on submission and `toLocaleString()` display.
- Question: Is the Monitor-specific logo part of this task? Answer: No. Log a
  separate future roadmap ticket for a user-supplied Monitor logo and a modest
  Roventics acknowledgement on the website.

## Change

- Increase the authenticated layout/card width responsively while preserving a
  usable mobile layout.
- Move the selected meter name and owner email into a compact header at the top
  of its workspace.
- Consolidate the most important forecast values into a prominent planning
  summary near the top: estimated current balance, remaining days, top-up-by
  date and recommended 30-day top-up amount.
- Keep the latest actual reading and observation time visible so estimates are
  never presented as meter facts.
- Refactor manual ledger management into accessible Material UI tabs for
  balance records and top-up records near the bottom of the workspace. Each tab
  owns its matching entry action and records without changing API contracts.
- Add icons to the primary navigation, search, create, save, edit and delete
  actions while retaining text labels and accessible names.
- Add `@mui/icons-material` at the installed Material UI version and update the
  dependency lockfile.
- Remove `ReminderSettingsPanel` from the selected-meter experience and stop
  loading or saving reminder settings from the frontend. Remove frontend code
  that becomes unused, but do not change reminder backend behavior or data.
- Preserve UTC API submission/storage and browser-local input/display behavior;
  add or adjust frontend checks for representative UTC-to-local rendering.
- Update the frontend README and repository context with the new information
  hierarchy and the intentionally hidden reminder controls.

The coordinated layout and removal of unused reminder code exceed the usual
100-line implementation target. Keep them in this one approved UI task so the
selected-meter flow and its cleanup can be reviewed together; backend and data
contracts remain outside the change.

## Reuse

- Reuse the existing Material UI theme, authenticated layout and selected-meter
  state in `software/frontend/src/App.tsx`.
- Reuse `ForecastPanel` forecast labels and unavailable-state handling rather
  than duplicating forecasting calculations in the browser.
- Reuse `LedgerPanel`, its API mutation callbacks, datetime helpers and existing
  edit/delete confirmation behavior.
- Reuse the current dashboard API response; do not add a backend aggregate or
  alter forecasting formulas for presentation needs.
- Reuse the backend reminder constants and opt-in delivery behavior unchanged.

## Verify

- Run the focused frontend test suite and add coverage for the prominent
  planning summary, meter/owner header, balance/top-up tabs, icon-labelled
  actions and absence of reminder controls/requests.
- Verify valid, unavailable and inconsistent forecast states remain honest and
  the latest actual observation remains visible.
- Verify a submitted local datetime is sent as UTC and returned UTC timestamps
  render through the browser's local timezone.
- Run the frontend production build and `git diff --check`.
- Confirm the backend reminder files, API and database migration are unchanged.

## Out of scope

- Changing forecast formulas, database schemas, raw SQL, backend dashboard
  responses or meter authorization.
- Enabling reminders by default, changing existing reminder opt-ins, adding a
  reminder scheduler UI or changing reminder delivery cadence.
- Adding tariffs, Rand values, payments, OCR, hardware, MQTT or ML.
- Creating, selecting or installing the future Monitor-specific logo or changing
  the existing Roventics acknowledgement/branding in this task.
- Modifying either sibling repository.
