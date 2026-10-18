# Forecasting research

One normal entrypoint, simulator.py, runs this offline experiment. It generates
fictional observations/truth, fits one rolling consumption line and shows or
exports the results. It never imports the app or accesses its database.
Matplotlib 3.11.2 and NumPy 2.5.4 stay in this local environment; the pinned
requirements need Python 3.12+. Research and output stay outside Docker builds.

## Run

From the repository root in PowerShell:

```powershell
cd software/backend/research/forecasting
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe simulator.py
```

Defaults: 730 fictional days (two-year replay), 0.1 seconds/day, 90-day lookback,
seed 42 and Mid randomness. The speed is a nominal 100ms timer interval;
rendering adds wall-clock overhead. GUI playback uses TkAgg, so Python Tkinter and a desktop
display are required. Headless export uses Agg without a display. On Linux/macOS use
`.venv/bin/python` instead.

```powershell
# Optional shorter lookback or another starting slider level; still a two-year replay.
.\.venv\Scripts\python.exe simulator.py --lookback 60 --randomness high

# No wall-clock delay: export all three randomness levels.
.\.venv\Scripts\python.exe simulator.py --headless --output out/task055-730-90
.\.venv\Scripts\python.exe simulator.py --headless --lookback 60 --output out/task055-730-60
```

Options: `--days` (positive integer; default 730), `--lookback` (60/90;
default 90), `--randomness` (low/mid/high; default mid), `--seconds-per-day`
(default 0.1, CLI only), `--seed` (default 42), `--headless` and `--output`
(default out/randomness).
Headless export covers every level, regardless of the initial GUI level.
Use distinct output directories to preserve earlier runs.
Two years is the replayed synthetic history, not a reliable two-year forecast.
The prediction horizon remains 30 days; longer playback does not establish
accuracy. The research check script was removed at the user's request; only
manual/native/headless smoke verification is used for this change.

## Simple replay

The window has exactly two graphs: remaining balance and total consumed energy.
They distinguish synthetic truth revealed so far, actual recorded observations,
reconstructed consumption with inferred connections and the future estimate.
No future truth or purchase is passed into the model; future balance assumes
no further purchases.
An orange band in both graphs marks the moving 60/90-day context from
max(simulation start, now − lookback) through now. It highlights the recent
window available to the rolling fit, not a future forecast or confidence band.

Three headline figures show estimated balance, remaining days and
"Predicted monthly requirement (30 days)": the existing consumption_30 value,
daily usage estimate × 30, independent of the current balance. It is total
predicted use, not the extra purchase needed now. A small date/source label
distinguishes a learned rate from an assumed default. Controls are Play/Pause,
Reset and the single bottom
Low/Mid/High randomness slider. There is no household selector, GUI speed control,
manual-entry controls or technical error sidebar. Detailed errors stay in exports.

The slider changes variability, not electricity-usage classes. Every level uses
the same nominal 10 kWh/day household basis; daily consumption variation and
purchase-interval jitter both increase with randomness. Actual sampled averages
can differ over a finite run. Independent usage/purchase/reading random streams
preserve reproducibility. Changing level restarts with the same seed and clears
that run's scores; it never retrains the frozen separate training prior. Reset
and a changed slider level restart paused, recording the known configured
starting balance before the first render. This is one known starting observation,
not invented earlier history. The labelled frozen default gives an immediate
monthly estimate (about 301.4 kWh at the current assumed 10.046 kWh/day) until
valid readings support a personal rate. Bare empty simulations/forecasts and
the headless replay pipeline are unchanged; without a known balance they still
cannot predict. Task 054 changes GUI startup/display only; verification is below.

| Randomness | Daily rate before Wh rounding | Scheduled attempt gap |
| --- | --- | --- |
| Low | 10 ± 10% (9–11 kWh/day) | 240 ± 24 hours |
| Mid | 10 ± 40% (6–14 kWh/day) | 240 ± 96 hours |
| High | 10 ± 80% (2–18 kWh/day) | 240 ± 192 hours |

One uniform usage draw is made per fictional day; its hourly energy is rounded
to integer Wh using nearest/ties-to-even rounding. Separate usage, purchase-timing,
purchase-amount and reading streams are keyed by cohort/seed, not level, allowing
paired comparisons. Readings stay 12–336 hours apart. Scheduled gaps are attempt
intervals, not guaranteed actual purchase gaps: the safeguard and skipped
purchases change realised timing. Higher randomness need not mean more purchases.

Initial balance is 300 kWh. Purchases add 150–350 kWh, skip when stock exceeds
250 kWh and have a below-50 kWh safeguard. This bounds stock near 600 kWh and
avoids physical run-out; randomness is not a missed-record or outage probability.
These are simulation rules, not purchasing advice. Dense hourly truth remains
separate from irregular balance observations.

## Unchanged forecast and scoring rules

Reconstruct consumption only from known observations, counting purchases in
`(previous balance time, current balance time]`:

```text
interval_use = previous_balance + interval_purchases - current_balance
cumulative_use[i] = cumulative_use[i-1] + interval_use
fit: cumulative_use = rate * actual_elapsed_days + intercept
```

Use one ordinary least-squares line through actual balance observations in the
last 90 days, optionally 60. The implementation uses
[NumPy least squares](https://numpy.org/doc/stable/reference/generated/numpy.linalg.lstsq.html),
not segmentation, blending or ML. Integer-Wh generation conserves energy;
reconstruction uses Decimal kWh and the fit/projections use floating point.

No balance means no prediction. Two distinct valid in-window readings allow
fitting; otherwise the linear experiment labels its frozen training default.
That prior is calibrated separately from fictional training ledgers and stays
independent of demo duration, seed, level, lookback and reset. Fixed 10 kWh/day
remains a comparator, not a claim of known household usage. The mean comparator
requires two actual readings. Invalid/contradictory history is surfaced, not
repaired with a default. Zero use is valid with no finite run-out date.
The current training configuration is five separate Mid-randomness households,
90 days each, seeds 9173–9177, with the median of their observed ledger rates
frozen before GUI playback. It yields approximately 10.046 kWh/day; this new
generator's calibration is not Task 052's older cohort result.

```text
balance_now = max(0, latest_actual + known_later_purchases - rate*elapsed_days)
days_remaining = balance_now / rate                 # no finite date if rate=0
usage_30_days = rate * 30
additional_top_up = max(0, usage_30_days - balance_now)
```

Balance is anchored to the latest actual reading, never the fitted intercept.
There is no buffer. For example, 15 kWh/day with 300 kWh left means 20 days,
450 kWh total 30-day use but only 150 kWh additional purchase.
The GUI's monthly headline is 450 kWh at that rate even after a purchase leaves
no additional energy to buy. The separate additional_top_up/top_up_30 formula
and exports remain unchanged. Monthly requirement updates when the estimated
rate changes; there is no smoothing or forced positive minimum. Genuine zero
usage can show 0 kWh; invalid/unavailable histories withhold the estimate.

New readings are scored before assimilation. At 00:00 UTC on each month's last
calendar day, score the current-balance estimate from the pre-reading ledger.
This is not a balance forecast issued a month earlier. Freeze its next-30-day
consumption forecast; score only after the entire horizon is revealed. Future
horizons remain pending. Signed errors are prediction minus truth.

Headless outputs retain signed/absolute reading and month-end errors, MAE, bias,
scored/pending/unavailable counts and baseline/default comparisons for every
randomness level. Compare only like-for-like available observations. Yearly
month-end samples do not establish every-day accuracy.

```text
out/<run>/
  manifest.json
  summary.json
  <level>.png
  <level>-monthly.csv
  <level>-readings.csv
```

Outputs and .venv/ are ignored. Generated files are synthetic review artefacts,
not app fixtures. PNG bytes need not match across platforms/fonts.

## Verification, history and limits

Task 055's default 730/90 headless smoke passed at all three levels; all three
PNGs decoded and the final 90-day orange band was visually checked. Each level
has 24 month-end snapshots, 23 matured horizons and one pending. An explicit
180/90 rerun's eight JSON/CSV reports match Task 054 byte-for-byte. Native 100ms
Play/Pause and both orange context bounds at days 180/700 with 60/90-day
lookbacks passed; the future horizon stays 30 days. No removed suite ran for this
change. Prior checks and annual numbers below are historical, not two-year
validation or evidence of two-year forecast reliability.

Task 054 passed all 23 focused checks and four native GUI check groups. Launch,
Reset and every slider level show one known starting balance with an immediate
Assumed default monthly estimate; Play does not duplicate that starting record.
The 15 kWh/day case keeps 450 kWh monthly requirement while extra purchase falls
from 150 to zero. Genuine zero, invalid withholding, label fit and native 500ms
Play/Pause were checked; the owned window/timer closed. A 180/90 headless rerun's
eight JSON/CSV reports are byte-identical to Task 053's corresponding run, so
this display/startup change provides no new accuracy benefit.
The evidence below remains Task 053's unchanged headless model/generator result.

Task 053's 20 focused checks passed. Headless 180/90, 365/90 and 365/60 runs
each exported all three levels (nine PNGs total). Native GUI verification passed:
500ms timer, mouse Play/Pause/Reset, all slider positions, same-seed/frozen-prior
reset of populated run records/scores, two graphs and three correct estimates.
Owned-window captures were checked and the window closed. Seed 42 annual
matured month-end 30-day consumption MAE in kWh is:

| Randomness | 90-day lookback | 60-day lookback |
| --- | ---: | ---: |
| Low | 2.0451 | 2.3685 |
| Mid | 8.0717 | 9.3970 |
| High | 16.1019 | 18.7709 |

Each annual level has 12 month-end snapshots, 11 fully matured horizons and one
pending horizon. In this independent-daily-noise example, 90 days had lower MAE
than 60; that is not a general window-selection rule or household accuracy claim.
The baselines beat the rolling line at every level: for Mid, annual 30-day MAE
is 8.0717 kWh (linear), 7.8282 (all-history mean) and 6.1811 (fixed 10).
The calibrated prior is also worse than fixed 10 at each level's one cold-start
score; Mid absolute error is 4.7409 versus 4.529 kWh. This stationary independent-
noise example does not establish an accuracy benefit for the model or prior.
It is a UI/data simplification, not an adoption decision.
Do not reuse the older scenarios' figures as performance of this new generator.
[Task 052 results](../../../../agents/work/052-linear-forecast-simulator/changes.md)
retain the previous interface, calibration and metrics as historical evidence.

Task 053 retired generate.py, plot.py and checks.py after dependency review
and verified exact-byte archival in ignored .tmp/task053/legacy-research.zip.
That retained local ZIP contains all three sources; recovery cannot rely on Git
because they were untracked. Extract to a separate staging directory and compare
the recorded hashes before restoring any source. See the
[recovery record](../../../../agents/work/053-simple-randomness-replay/changes.md)
for exact paths and recovery checks. Existing outputs, environment and work
history are preserved. At the user's request, Task 055 also removed
simulator_checks.py after retaining its exact bytes at
.tmp/task055/simulator_checks.py. Its recovery hash/details are in the Task 055
work record; it is an ignored local backup, not a runnable current suite or Git
backup. No current command invokes it.

Tickets 66.1/66.2 completion, 66.3 review, full 66.4 held-out criteria/go-no-go and
66.5 fresh integration approval remain open. Broader mistakes/missing-purchase,
seasonality and exhaustion cases need separate evidence. These controlled
examples cannot establish real household accuracy. The live app keeps its
current model and Not enough data policy. No integration or automatic adoption.
