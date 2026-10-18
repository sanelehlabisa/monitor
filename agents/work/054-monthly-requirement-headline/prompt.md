# Task 054: Monthly requirement headline

## Aim

Show the predicted full 30-day electricity requirement from the first known
starting balance, rather than the changing extra purchase needed now.

## Clarifications

- Monthly requirement = estimated daily usage x 30, regardless of current balance.
- Show it immediately after recording the configured starting balance, using the
  labelled frozen default until observations support a personalised rate.
- Update with the usage estimate; do not artificially smooth or hold it constant.

## Change

- In the research GUI, replace the additional-top-up headline with
  "Predicted monthly requirement (30 days)", using existing consumption_30.
- On GUI launch/reset, record the known configured starting balance through the
  existing recording method, so estimates are available before pressing Play.
  Do not invent earlier readings or change the empty-ledger forecasting policy.
- Preserve the separate additional-purchase formula/exports, forecast algorithm,
  frozen calibration, randomness control, 0.5-second timer and two graphs.
- Keep invalid histories unavailable and genuine zero usage valid; do not force
  a positive number merely to keep the headline populated.
- Update relevant research documentation/context and record results in changes.md.

## Reuse

- Existing consumption_30, record_balance, GUI rendering and focused checks.

## Verify

- At 15 kWh/day, show 450 kWh before/after a purchase even when extra needed is zero.
- Verify immediate labelled starting estimates, updates from changed readings,
  reset/slider behaviour, no duplicate starting records and empty/zero states.
- Run focused checks and a native GUI check; confirm unchanged live files and
  clean diff whitespace. Keep implementation within 100 changed lines.

## Out of scope

- Live application/API/DB changes, model/calibration changes, smoothing, buffers,
  new dependencies, extra UI controls, siblings, commits and pushes.
