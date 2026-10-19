# Task 067: Date Label Cleanup

## Aim

Remove the visible timezone suffix from the monthly top-up date.

## Clarifications

- Requested wording-only change: remove " (UTC)"; preserve the date and UTC calendar logic.

## Change

- Remove the suffix in ForecastPanel and update its wording assertion.
- Record results and update relevant current documentation.

## Reuse

- Existing utcDateDisplay, ForecastPanel and frontend checks; no new helper.

## Verify

- Run frontend checks/build; confirm the suffix is absent and the UTC calendar-date tests still pass.

## Out of scope

- Calculation, API, timezone, layout, deployment, reminder or dependency changes; live data/mail/service actions; commits/pushes.
