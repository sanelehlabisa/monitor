# Task 052: Linear forecast simulator

## Aim

Build one offline Python simulator to inspect per-meter linear forecasts and
month-end prediction errors before considering application integration.

## Clarifications

- Timing: one fictional day per 5-10 seconds, adjustable faster for testing.
- Duration: 180 days by default, with a 365-day option for yearly inspection.
- Model: use the latest 90 days, optionally 60, to forecast the next 30 days.
- Starting rate: begin with 10 kWh/day, calibrate a replacement using separate
  fictional training households, then freeze it for different demo households.
- No predictions without a recorded balance. Recalculate after additions or
  deletions. Keep all new runnable behaviour in one script; preserve old utilities.

## Change

- Add `software/backend/research/forecasting/simulator.py`, containing generation,
  calibration, reconstruction, regression, replay, scoring and Matplotlib GUI.
- Generate seeded low/medium/high, constant, gradual and sudden-change examples
  with random purchases and irregular readings. Observations contain device_id,
  timestamp, event_type and value_kwh; dense truth stays separate and conserved.
- Calibrate one starting rate as the median of training households' observed
  consumption/elapsed-day rates. Use separate IDs/seeds/parameters from the demo;
  freeze calibration independently of demo duration, lookback, selection or reset.
  Keep 10 kWh/day as the labelled initial/fallback and comparison, not a claimed
  real-household rate. Calibration need not outperform 10; report actual results.
- Reconstruct consumption using previous balance + purchases - current balance,
  counting purchases in (previous, current]. Validate UTC times and finite kWh;
  surface contradictory history instead of silently repairing it with a default.
- Fit one `y = mx + c` using actual elapsed days and only available balance
  observations inside the selected rolling window. Two distinct valid readings
  permit fitting; otherwise use the labelled frozen default. No segmentation,
  blending, periodic model or ML. Rates cannot be negative; zero use is valid.
- Anchor balance estimates to the latest actual balance plus known later purchases
  minus estimated subsequent consumption, not the fitted intercept. Calculate
  current balance, days remaining, 30-day consumption and additional top-up with
  no buffer. Zero use has no finite run-out; no balance means unavailable.
- Show two updating graphs: actual/recorded/estimated/future balance with purchase
  markers, and actual/reconstructed consumption with the fit and 30-day extension.
  Label actuals, estimates and the assumed default separately. Reveal truth only
  through simulated now; never give hidden truth or future events to the model.
  Future balance assumes no further purchases. A compact panel shows simulated
  date, rate/source, balance, remaining days, 30-day usage/top-up and forecast error.
- Include Play/Pause/Reset, adjustable speed and scenario selection. Add Record
  balance now/Delete latest balance controls to demonstrate immediate refitting;
  simulated top-up records arrive automatically. Deletions affect observed records,
  not hidden physical truth. Preserve past forecast/error snapshots unchanged.
- Score new readings before fitting them, accounting for known intervening
  purchases. Report signed/absolute calendar month-end balance errors and 30-day
  consumption errors matured only after their horizon is revealed. Include kWh
  MAE, bias and scored/pending counts by scenario/month. Yearly summaries describe
  month-end forecasts, not every-day accuracy; late horizons remain pending.
- Compare with fixed 10 kWh/day and the existing consumption/elapsed-time baseline
  on the same available records. Provide a headless replay/export option for PNGs
  and reproducible error summaries under ignored `out/`; GUI uses the same maths.
- Reuse the research environment and declare NumPy only in research requirements.
  Update launch instructions, equations, limitations, current roadmap/context and
  actual checks in changes.md. Keep Ticket 66 IDs; replace its current segmented
  candidate scope with this single-line experiment without closing the full
  validation/adoption gates. Preserve uncommitted Tasks 050-051 work.
- Review-size exception: allow up to 650 implementation lines for this complete
  self-contained numerical/replay/GUI experiment; tests/docs/outputs are excluded.
  Do not compress code to meet the limit; request a split if more is necessary.

## Reuse

- Existing research environment, ignored output layout, seeded generation and
  checked UTC/kWh/top-up-boundary patterns; preserve generate.py, plot.py and checks.py.
- Matplotlib/NumPy, standard-library checks and the existing forecasting equations.
  Do not import plot.py, which forces a non-interactive backend, into the GUI.

## Verify

- Check reproducibility, energy conservation, independent training/demo inputs,
  hand-calculated forecasts, 60/90-day boundaries and zero/invalid/sparse histories.
- Check no predictions before a balance, no future-data leakage, additions/deletions,
  pre-update scoring, immutable errors and incomplete/pending horizon handling.
- Run 180/365-day headless examples and existing research checks; inspect images,
  month-end error summaries and GUI controls, and report any unavailable checks.
- Check output/build exclusions, unchanged runtime files and git diff --check.

## Out of scope

- Application/API/UI/database changes, live cold-start policy changes, production
  integration, automatic adoption, real/demo DB writes, runtime dependencies,
  hardware/OCR/ML, tariffs/payments, Docker restarts, siblings, commits and pushes.
- Stop after the simulator and its evidence; integration needs fresh approval.
