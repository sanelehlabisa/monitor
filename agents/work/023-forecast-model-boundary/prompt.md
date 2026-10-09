# Task 023: Forecast model boundary

## Aim

Create one replaceable forecasting function and implement its first transparent
daily-usage calculation without coupling callers to the calculation method.

## Clarifications

- Question: How can forecasting change later? Answer: API and UI code will call
  one public `run_forecast_model` function defined in one backend module.
- Question: Is the first model ML? Answer: No. It is deterministic math behind a
  model-shaped boundary and may be replaced later without changing consumers.
- Question: How are multiple readings used? Answer: Use a time-weighted rate
  across all adjacent valid balance intervals and include interval top-ups.
- Question: What happens with invalid history? Answer: Return explicit
  `not_enough_data` or `inconsistent_history` states, never a guessed rate.

## Change

- Add typed input/output dataclasses and one public model entry point.
- Sort factual events, evaluate adjacent balance intervals and allocate top-ups
  using `previous < top_up_time <= current` boundaries.
- Calculate time-weighted daily usage with Decimal arithmetic.
- Treat fewer than two balances, non-positive elapsed time and negative implied
  consumption as explicit non-forecast states.
- Add focused pure unit tests for ordering, top-ups, multiple intervals, zero
  consumption, insufficient data and inconsistent history.

## Reuse

- Reuse the existing balance/top-up dataclasses, timezone rules and Decimal kWh
  conventions; add no persistence or dependency.

## Verify

- Run focused forecast tests, then the complete backend suite.
- Run `git diff --check`.

## Out of scope

- Current-balance projection, remaining days, run-out date, recommendations,
  HTTP routes, UI, reminders, ML training and stored forecast output.
