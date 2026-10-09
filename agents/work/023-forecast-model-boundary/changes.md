# Task 023: Forecast model boundary

## Result

Forecast consumers now have one replaceable `run_forecast_model` function. Its
first implementation derives a deterministic daily-use rate from factual
ledger history without introducing ML or persistence.

## Change and reuse

- Added typed forecast status/result contracts in one focused domain module.
- Reused existing immutable balance/top-up records, timezone-aware timestamps
  and Decimal kWh values.
- Sorts facts, validates every adjacent interval, includes top-ups using
  `previous < occurrence <= current`, and returns a time-weighted rate.
- Returns explicit insufficient or inconsistent states instead of skipping bad
  history or guessing.

## Verification

- Focused pure forecast tests: 4 passed.
- Complete backend suite: 48 passed.
- `git diff --check` passed with only line-ending notices.
