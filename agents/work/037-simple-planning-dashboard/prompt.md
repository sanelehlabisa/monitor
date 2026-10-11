# Task 037: Simple planning dashboard

## Aim

Simplify the selected-meter UI around the user's example (Ticket 60).

## Clarifications

- Predictions first; show forms, history and settings only when requested.
- Keep the run-out date below remaining days and label the latest actual reading.

## Change

- One responsive planning card: estimated balance, days remaining and monthly
  purchase recommendation, with a compact meter-name/owner heading.
- Keep the existing recommendation: additional kWh needed for the next 30 days,
  accounting for estimated balance. Never use the example's illustrative numbers.
- Add two large icon buttons: Record balance and Record top-up. Each reveals
  only its matching existing form, with cancel/close and existing save behavior.
- Collapse history, meter settings and calculation details below; keep latest
  actual reading/time, estimate timestamp, unavailable states and retry visible.
- Reuse Material UI and current styling. Update README/context and changes.md.
  Allow up to 200 changed implementation lines to replace clutter and gate the
  existing forms across components; no architecture rewrite.

## Reuse

- ForecastPanel, LedgerPanel, MeterWorkspace, dashboard refresh/save handlers,
  date helpers and existing MUI icons; backend math and raw SQL stay unchanged.

## Verify

- Check desktop/mobile layout, hidden-by-default sections, both record actions,
  cancel/save/correction, forecast refresh and honest empty/error/zero-use states.
- Use synthetic data only. Run relevant frontend checks, build and diff check;
  remove only this task's demo data and record actual results.

## Out of scope

- Backend/model/database changes, dependencies, new branding, reminders,
  deployment, tariffs, payments, hardware/OCR/ML. No commit/push without a new request.
