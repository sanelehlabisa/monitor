# Task 024: Forecast projections

## Result

The single forecast-model function now returns the complete deterministic V1
planning projection while retaining explicit unavailable states.

## Change and reuse

- Extended Task 023's result rather than adding a second model path.
- Added latest-actual basis, calculation time, estimated current balance,
  remaining days, run-out time and recommended 30-day top-up.
- Later top-ups are included through `as_of`; later top-ups are ignored and an
  `as_of` before the latest actual balance is inconsistent.
- Zero use has no finite run-out and a zero recommendation. Exhausted estimates
  clamp energy/days to zero instead of displaying negative values.
- The recommendation has no hidden safety buffer.

## Verification

- Focused pure forecast tests: 8 passed.
- Complete backend suite: 52 passed.
- Covered later top-ups, depletion, zero usage, naive/backward times and
  time-zone-equivalent calculation times.
- `git diff --check` passed with only line-ending notices.
