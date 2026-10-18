# Task 052: Linear forecast simulator

Implemented after approval on 2026-10-18. Research only; no commit or push.

## Changes and reuse

- Added one runnable `software/backend/research/forecasting/simulator.py` with
  seeded household generation, training-default calibration, consumption
  reconstruction, one rolling OLS line, chronological replay, GUI and exports.
- Uses 180 days/90-day lookback/10 seconds per fictional day by default; 365 days,
  a 60-day lookback and speeds down to 0.1 seconds/day are configurable. The
  forecast horizon stays 30 days. GUI starts paused with an empty observed ledger.
- Separate training households use seed 9173 and 90 days. The frozen median
  observed ledger rate is 6.960 kWh/day; 10 remains the initial/fallback and fixed
  comparator. No demo values, truth or errors enter calibration. No balance means
  no prediction; sparse valid histories use the labelled research default.
- Reused the existing checked kWh/UTC and `(previous, current]` purchase rules,
  latest-actual balance anchor and 30-day additional-purchase equation. Retained
  generate.py, plot.py and checks.py unchanged. The simulator does not import
  plot.py, app modules or application dependencies.
- Household facts use device_id/timestamp/event_type/value_kwh. Exact integer-Wh
  generation and Decimal reconstruction keep truth/ledger energy conserved;
  NumPy performs the floating-point fit. Centering cumulative values before OLS
  prevents a flat recent window from producing a tiny false positive usage rate.
- Fictional balances start at 300 kWh. Readings are 12-336 hours apart; purchase
  attempts have random gaps/150-350 kWh amounts, skip balances above 250 kWh and
  retain a below-50 kWh safeguard. These controlled examples do not exhaust supply.
- GUI provides Play/Pause/Reset, speed, household selection and Record/Delete
  latest balance. Edits refit surviving observations without rewriting truth or
  past prediction/error snapshots. Assumed defaults, actuals and estimates are
  labelled; future balance assumes no further purchases.
- Scores new readings before assimilation. Calendar month-end current-balance
  checks occur at 00:00 UTC on the last day, before a same-time balance reading.
  Separate 30-day consumption forecasts mature only when those days are revealed.
  CSVs include signed/absolute errors; JSON contains MAE, bias and scored/pending/
  unavailable counts, plus a matched cold-start comparison. This is not fitting
  loss or every-day annual accuracy. Fixed 10 and the all-history mean are explicit
  comparators; the latter keeps its two-reading requirement.
- Added explicit simulator_checks.py outside normal backend test discovery.
  Declared the already-installed NumPy 2.5.4 directly beside Matplotlib 3.11.2 in
  research requirements only; combined pinned requirements need Python 3.12+.
- Updated root/software/backend/research READMEs and agents/context.md. Kept
  Ticket 66 IDs; the current 66.3 scope is rolling linear, not the earlier
  segmented proposal. Historical Tasks 050/051 and their uncommitted work remain.
- Review-size exception used: 536 simulator source lines plus one dependency
  line = 537 implementation/config lines, below the approved 650-line cap.
  Checks, documentation and generated artifacts are excluded from that count.

## Verification actually run

- Existing `checks.py`: all 12 checks passed. New `simulator_checks.py`: all 17
  checks passed, including a final rerun after generation/error-column fixes.
  Coverage includes seeded/prefix reproducibility, exact energy conservation,
  training/demo isolation, hand equations, irregular OLS/intercept anchoring,
  inclusive 60/90-day boundaries, zero/sparse/invalid histories, timezone
  equivalence, future-record exclusion, pre-update errors, immutable edits,
  pending horizons and summary counts. Poisoning unrevealed truth did not affect
  fitting/scoring before its horizon; removing training truth did not affect
  calibration.
- Research `pip check` passed. Research Python is 3.14.4; Tk 8.6, Matplotlib
  3.11.2 and NumPy 2.5.4 are available in the ignored local environment.
- Headless runs passed for 180 days/90-day window and 365 days with both 90/60-day
  windows. All five scenarios ran each time; all 15 resulting PNGs decoded.
  Repeating the annual 90-day run in another output directory reproduced all
  12 JSON/CSV reports byte-for-byte. PNG bytes are not a portability contract.
- Visually inspected representative annual plots and final native GUI captures.
  Actual Matplotlib mouse events and the native Tk timer verified Play/Pause,
  advancement, pause stability, Reset, 5/10/0.1-second speeds, scenario selection,
  record/delete, immediate refitting and unchanged frozen calibration. Final
  repeat passed after increasing plot/button spacing. The owned window, figure
  and timer were closed; no desktop-wide screenshot was taken.
- `git diff --check` and an explicit new-source trailing-whitespace check passed.
  Git ignores out/, .venv/ and .tmp/; research remains excluded from Docker.
  Runtime app/tests/requirements/Dockerfile/Compose/frontend/database diff check
  passed unchanged. No backend/frontend runtime suite or Docker restart was
  needed for this isolated experiment; no services or database were touched.

## Observed errors and limitations

Seed 42; MAE in kWh for matured month-end next-30-day consumption forecasts:

| Scenario | 90-day line | 60-day line | All-history mean |
| --- | ---: | ---: | ---: |
| Gradual change | 66.13 | 51.16 | 128.48 |
| Sudden change | 103.82 | 78.20 | 134.35 |

- Constant-profile 30-day MAE is below 1e-9 after learning: these deliberately
  easy, noise-free Wh-quantized rates do not establish real household accuracy.
  The shorter window adapts faster in these examples, not necessarily elsewhere.
- Each annual scenario has 12 month-end issues, 11 matured horizons and one
  pending. The 180-day runs have six issues, five matured and one pending.
- The calibrated starting rate beats 10 on four of five first cold-start scores
  but is worse for high use: 60.114 versus 43.774 kWh error on one observation.
  This is tiny synthetic evidence, not a general improvement claim.
- Irregular observation density can influence OLS. Abrupt changes and steady
  drift cause lag; seasonality, noisy/manual mistakes and missing purchases need
  broader evaluation. The purchase safeguard prevents physical run-out, so real
  run-out accuracy is not established. No future purchases are assumed in the
  projected balance curves.
- Full 66.1/66.2 acceptance, 66.3 review, 66.4 held-out criteria/go-no-go and 66.5
  integration approval remain open. The live app still uses its existing model
  and Not enough data policy. No application integration is approved by this task.

## Local review and handoff

From `software/backend/research/forecasting/`:

```powershell
.\.venv\Scripts\python.exe simulator.py --days 365 --seconds-per-day 5
```

- Reports/images: ignored `out/simulator-180-90/`, `out/simulator-365-90/`,
  `out/simulator-365-60/` and repeat `out/simulator-365-90-repeat/`.
- Temporary native GUI helper, owned-window captures and results: ignored
  `.tmp/task052/`. Generated artifacts/local environment are retained, not staged.
- No unique source or drawings were deleted. No real/demo data, app/API/SQL,
  runtime dependency, sibling, Docker state, Git commit or remote was changed.
- Stop here for developer review. The next unallocated work number is 053;
  neither further implementation nor integration starts automatically.
