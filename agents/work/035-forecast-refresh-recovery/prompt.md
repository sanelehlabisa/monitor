# Task 035: Forecast refresh and recovery

## Aim

Refresh planning estimates on demand and prevent stale forecasts after failed
reloads (Ticket 59).

## Clarifications

- The user confirmed an icon-labelled Refresh button and withholding stale
  estimates after failed reloads, using the existing dashboard endpoint.
- Keep the PoC minimal: no timers, new dependencies or backend changes.

## Change

- Add Refresh near the planning summary; disable it during loading or saving.
- Reuse dashboard loading for manual refresh and post-save recovery. Keep the
  backend calculation timestamp visible in local time.
- On failed initial, manual or post-save loading, withhold estimates and show a
  clear retry state rather than an endless spinner. Retain already-loaded records.
- Retrying reads must not repeat a saved purchase or balance. Prevent late
  responses from restoring a meter after navigation away.
- Keep implementation changes within 100 lines; update README/context and record
  actual results in changes.md.

## Reuse

- getDashboard, applyDashboard, ForecastPanel, existing MUI icons and ledger flow.
- Existing frontend checks and Task 034's temporary live-demo tooling.

## Verify

- Live-check refresh, loading controls, failed initial/manual/post-save reads,
  successful retry without duplicate writes, and navigation during a request.
- Use synthetic data only and clean it up. Run relevant frontend checks,
  production build and git diff --check.

## Out of scope

- Automatic refresh, new forecast math, backend/database changes, deployment,
  branding, reminders, household trials, dependencies, tariffs, payments and
  hardware/OCR/ML. No commit or push without a separate request.
