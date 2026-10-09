# Task 024: Forecast projections

## Aim

Extend the single forecast-model function with the V1 planning projections.

## Clarifications

- Question: What is estimated current balance? Answer: Latest actual balance
  plus later top-ups, minus forecast usage through an explicit `as_of` time.
- Question: Is there a safety buffer? Answer: No initial hidden buffer; the
  transparent 30-day recommendation uses the forecast rate directly.
- Question: How are exhausted balances handled? Answer: Clamp estimated balance
  and remaining days to zero while retaining the calculated run-out point.
- Question: What if daily usage is zero? Answer: Keep the valid zero rate and
  estimated balance, return no finite run-out date and recommend zero kWh.

## Change

- Extend the forecast result with estimated balance, remaining days, run-out
  time and recommended 30-day top-up kWh.
- Ignore events after `as_of` and reject an `as_of` before the latest usable
  actual balance.
- Calculate `max(0, 30 * daily_usage - estimated_balance)` with no hidden buffer.
- Keep all outputs Decimal/timezone-aware and clearly separate actual inputs
  from estimates.
- Add exact examples and edge-case tests for later top-ups, depleted balance,
  zero usage and time-zone-equivalent inputs.

## Reuse

- Extend Task 023's one public function and result contract rather than adding a
  second forecasting path.

## Verify

- Run focused forecast tests, then the complete backend suite.
- Run `git diff --check`.

## Out of scope

- HTTP, database schema, UI, configurable buffers, seasonal logic, ML and
  reminders.
