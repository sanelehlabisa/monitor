# Task 034: Live demo flow check

## Aim

Verify the live meter-planning flow and document a repeatable demo (Ticket 56).

## Clarifications

- The user chose the live demo check before VPS deployment.
- Use temporary synthetic records and Mailpit; preserve existing household data.
- Prefer practical demo checks and reuse existing tests.

## Change

- Exercise sign-in, meter creation, both record tabs, edits/deletions, forecast
  refresh and reopening a meter.
- Demo: 100 kWh eleven days ago, 20 kWh purchased six days ago, and 80 kWh
  observed one day ago. Expect approximately 4 kWh/day, 76 kWh now, 19 days
  remaining and a 44 kWh recommendation for the next 30 days.
- Check unavailable/inconsistent/zero-use states, user isolation, admin access,
  search, mobile layout and UTC/local-time handling.
- Fix small demonstrated flow blockers within 100 implementation lines; log
  larger work separately.
- Document the walkthrough and actual results; clean up only this task's data.

## Reuse

- Compose, Mailpit, existing scoped APIs, run_forecast_model, Task 033 UI and
  existing integration checks.

## Verify

- Compare live forecasts with the example arithmetic, allowing for elapsed time.
- Record actual browser/API/database results and cleanup. Run relevant existing
  checks for any fixes and git diff --check.

## Out of scope

- Deployment, logos, reminder changes, new forecast methods, permanent demo
  data, household trials, new dependencies, tariffs, payments, hardware/OCR/ML.
