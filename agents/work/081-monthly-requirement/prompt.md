# Task 081: Show total monthly requirement

## Aim

Show a fourth compact estimate for total monthly energy without subtracting balance.

## Clarifications

- The user directly requested this small addition alongside the current amount.
- Monthly requirement = daily usage times the actual planning month's days.
  Additional top-up keeps the existing current-balance subtraction and zero clamp.
  Example: 10 kWh/day, 30 days and 100 kWh remaining means 300 kWh required,
  with 200 kWh extra to add.

## Change

- Add monthly_requirement_kwh to the existing backend forecast and API response.
  Use current Decimal precision; return null for unavailable estimates.
- Show Monthly requirement alongside Additional top-up, balance and days remaining.
  Reuse the current responsive grid, with no extra panels or controls.
- Update relevant current documentation and focused existing checks.

## Reuse

run_forecast_model, calendar planning duration, EstimateMetric and dashboard refresh.

## Verify

Check total requirement is independent of balance and later purchases, respects
calendar length/default/measured rates, and stays null for unavailable history.
Verify the API field, frontend labels, responsive grid, build and existing checks.

## Out of scope

Changing the existing additional top-up equation, reminder content/scheduling,
new dependencies, stored data/schema, service recreation, commits or pushes.
