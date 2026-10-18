# Task 053: Simple randomness replay

Approved and implemented on 2026-10-18. Verification completed below.
No commit, push or application integration was performed or authorised.

## Recovery recorded before retiring files

The three old source files are untracked; Git cannot recover them. Dependency
inspection found only old checks.py importing old generate.py/plot.py. Neither
simulator.py nor simulator_checks.py imports these files. Current documentation
commands will be updated; historical work records remain unchanged.

Verified exact archive: `.tmp/task053/legacy-research.zip` (ignored, retained).
Its three entries match the original SHA-256 values and byte lengths:

| File under software/backend/research/forecasting/ | Bytes | SHA-256 |
| --- | ---: | --- |
| generate.py | 5603 | 0C35986EF38BAD03BCDC2C9FEA34AD30397103718187895B39B9905E4E1D6FA7 |
| plot.py | 6040 | 1812C7F0CFD9C8D6A172CF360B2D822EA7A747E3D0129EAC151F68E274C6372E |
| checks.py | 11705 | 81CAB94C96F602D22360237F8623F31FA04133EAC9B9CBF67B2FE172E05FD864 |

Archive SHA-256: `10C882223CFEA59BDD378CC01ECAAADF19F75FB120DD270286A074FBA7701747`.
To recover, expand the archive into a new temporary directory, verify these
hashes and restore the three named files to the forecasting directory. Do not
overwrite the current simulator/checks. This local ignored backup is not a Git
backup and will not appear in a fresh clone. Previous outputs and .venv remain.

The pre-change simulator is also copied to ignored
`.tmp/task053/simulator-before.py` for exact review-size comparison and recovery.

## Implementation and checks

- `simulator.py` is the sole normal entrypoint; simulator_checks.py remains the
  focused verification suite. The three archived legacy scripts were deleted
  only after the recovery record above was written. Generated output, the local
  environment and historical work records were not deleted.
- One household now has a nominal 10 kWh/day basis at every randomness level:
  Low/Mid/High uses daily variation of +/-10/40/80% and purchase-attempt gaps of
  240 +/-24/96/192 hours. Usage is drawn once per day, rounded to integer Wh per
  hour and conserved exactly. Four separate usage/timing/amount/reading random
  streams use the same cohort/seed across levels for paired comparisons.
- Initial balance remains hardcoded at 300 kWh. Purchases add 150-350 kWh, skip
  stock above 250 kWh and retain the below-50 kWh safeguard. Actual purchases
  depend on these checks, so wider timing jitter need not increase their count.
  Randomness is not a missed-record or outage feature; supply never exhausts.
- Default playback is a 500 ms timer interval (0.5 seconds per day, with rendering
  overhead). The interface has only Play/Pause, Reset and the bottom three-stop
  randomness slider, plus the balance/total-consumption graphs and three planning
  values: estimated balance, remaining days and additional kWh for the next 30
  days. Date/default-source text is small; the native toolbar, scenario/speed/
  manual-entry controls and technical error sidebar are removed.
- Moving the slider restarts paused with the same seed and an empty ledger/new
  run scores. Calibration stays frozen. Five separate Mid training households,
  90 days each at seeds 9173-9177, produce a median observed rate of
  10.045816023738873 kWh/day. Task 052's old cohort/default and error numbers are
  historical only, not results for this changed generator.
- Kept the single 60/90-day OLS, latest-actual balance anchor, 30-day equations,
  assumed sparse-data default, no prediction before a balance, purchase interval
  boundaries, invalid/zero-history handling and chronological scoring unchanged.
  Detailed baseline/cold-start/month-end errors remain in headless CSV/JSON.
- CLI --randomness replaces --scenario; default output is ignored out/randomness/.
  Headless export runs all three levels. 180/365-day and 60/90-day options remain;
  --seconds-per-day is a CLI-only override. Dependencies are unchanged.
- Updated root/software/backend/research READMEs and agents/context.md while
  preserving stable Ticket 66 IDs, historical work and pending Tasks 050-052.
  Full validation and the separate integration gate remain open; next work is 054.
- Review-size exception used: main-source comparison against the preserved
  pre-change file is 95 additions and 110 deletions; retired generate.py/plot.py
  add 121+106 deleted implementation lines, totalling 432, below the approved
  650-line cap. The retired 207-line checks.py, current checks, docs and archives
  are excluded as tests/documentation/generated recovery artifacts.

## Verification actually run

- All 20 focused simulator checks passed in the independent run and root rerun.
  Retained forecast/equation/window/causality/scoring checks; added paired
  variability/purchase-jitter assertions and migrated exact UTC/repeated-boundary
  and two-graph PNG/figure-cleanup checks from the retired suite's relevant scope.
  This is the current 20-check suite, not a claim that the retired 12 also ran.
- Checked seeded generation/prefixes, exact hourly conservation, unchanged
  nominal use and reading cadence across levels, distinct training/demo data,
  graded daily variation, documented purchase jitter, bounded balances, sparse/
  zero/invalid histories, pre-update scoring, immutable forecast snapshots and pending
  horizons. No future records or hidden usage enter the model/calibration.
- Headless 180/90, 365/90 and 365/60 runs passed at all three levels. All nine
  PNGs decoded; representative plots were visually inspected. Repeating the
  annual 90-day run reproduced all eight JSON/CSV reports byte-for-byte.
- Research pip check passed; the existing local Python/NumPy/Matplotlib/Tk
  environment was reused without installing dependencies or changing runtime
  requirements. No backend/frontend runtime suite or Docker restart was needed.
- Final native Tk test used actual Matplotlib mouse events and the 500 ms timer.
  Verified Play/Pause, advancement and pause stability, Reset reproducibility,
  all three slider positions, same seed/prior, and clearing records/errors/month
  issues/estimate snapshots after a real 35-day engine run. Three displayed
  values matched the current forecast. There are exactly two data axes and
  three control axes, with no removed controls/sidebar/toolbar.
- Own-window and figure captures at 1400x920 were inspected: no overlap or
  clipping. Temporary helper/evidence is ignored under .tmp/task053/. Its owned
  native window, timer and figures closed in finally; final helper exited zero.
- Archive hashes/contents verified before retirement; the retained ZIP hash
  remains unchanged. No live imports or runnable documentation commands reference
  the retired scripts. Git ignores the archive, outputs and .venv; research stays
  excluded from Docker. Whitespace and unchanged-production diff checks passed.

## Observed results and limitations

Seed 42; annual matured month-end next-30-day consumption MAE, in kWh:

| Randomness | 90-day line | 60-day line | All-history mean | Fixed 10 |
| --- | ---: | ---: | ---: | ---: |
| Low | 2.0451 | 2.3685 | 1.9785 | 1.5578 |
| Mid | 8.0717 | 9.3970 | 7.8282 | 6.1811 |
| High | 16.1019 | 18.7709 | 15.6592 | 12.3360 |

- Each annual level has 12 issues, 11 matured horizons and one pending. Half-year
  runs have six issues, five matured and one pending. These are month-end sample
  errors, not every-day accuracy or in-sample regression loss.
- Fixed 10 and the mean outperform the rolling line on this stationary daily-noise
  dataset. The calibrated starting rate is also slightly worse than 10 on each
  first cold-start score, e.g. Mid 4.7409 versus 4.5290 kWh on one observation.
  Do not claim model/default improvement or justify adoption from this UI change.
- Increasing variability increases errors in this paired example. The 90-day
  window beats 60 here, not universally. Independent daily draws around a fixed
  nominal mean do not establish adaptation to seasonality or persistent drift.
- The safeguard prevents physical exhaustion; these runs do not validate missed
  purchases or real run-out error. Future balance still assumes no later top-ups.
  No household data, production policy or model integration changed.

## Local review and handoff

From software/backend/research/forecasting/:

```powershell
.\.venv\Scripts\python.exe simulator.py
```

Fresh ignored outputs are out/task053-180-90/, out/task053-365-90/,
out/task053-365-60/ and out/task053-365-90-repeat/. Old outputs are retained.
The removed three scripts are recoverable from the local archive above; it is
not present in a fresh Git clone. No other source or unique drawings were removed.
No app/API/DB/runtime dependency, sibling, service, Git commit or remote changed.
Stop for developer review; do not automatically start another task/integration.
