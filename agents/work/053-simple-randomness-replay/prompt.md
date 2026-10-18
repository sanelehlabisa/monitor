# Task 053: Simple randomness replay

## Aim

Simplify the standalone forecasting simulator around random consumption/top-ups,
two graphs and three clear planning estimates.

## Clarifications

- One main runnable script; default playback is 0.5 seconds per fictional day.
- Low/Mid/High means variability, not low/high average electricity usage.
- One bottom slider controls consumption changes and purchase-interval variation.
- A fixed starting balance is sufficient. No missed-top-up feature or controls.
- Show balance, days remaining and additional kWh needed for the next 30 days;
  retain both balance and total-consumption graphs.

## Change

- Keep simulator.py as the sole normal entrypoint. Replace visible household
  scenarios with one seeded household and a Low/Mid/High randomness slider.
  Keep the same nominal usage basis across levels; vary daily consumption and
  purchase timing using independent random streams and documented ranges.
- Retain the bounded purchase policy/energy conservation; randomness is not a
  missed-record probability or outage feature. Purchases affect balance, not
  inferred consumption. The model cannot see future events or hidden truth.
- Changing randomness restarts the demo and clears that run's scores, without
  changing its seed or retraining the separately calibrated frozen default.
- Keep Play/Pause/Reset, two readable graphs and the three headline estimates.
  Remove the scenario selector, GUI speed control, record/delete buttons and
  technical error sidebar. Retain a small date/default-source label; preserve
  detailed errors and baseline comparisons in headless exports instead.
- Preserve the single 60/90-day regression, 30-day equations, no-prediction-before-
  balance rule and chronological scoring. Default duration remains 180 days with
  a 365-day option. No forecasting algorithm replacement or live-app integration.
- Before retiring generate.py, plot.py and checks.py, verify dependencies and
  archive their exact bytes with hashes under ignored .tmp/task053/. They are
  untracked, so recovery cannot rely on Git. Record recovery before deleting only
  those three files. Preserve simulator_checks.py, outputs, venv and work history;
  retain relevant numerical/plot checks in the simulator's focused check file.
- Update current run instructions, context, stable Ticket 66 references and
  changes.md. Keep earlier results historical; rerun changed examples rather
  than presenting Task 052's numbers as the new simulator's performance.
- Allow up to 650 changed implementation lines, including old-script deletion,
  for this generator/GUI consolidation. Tests/docs/archives are excluded; split
  and seek approval if the limit cannot be met without compressed code.

## Reuse

- Existing simulator, independent checks, frozen calibration, research environment,
  UTC/kWh boundaries and ignored output/export workflow. Add no dependencies.

## Verify

- Verify archive contents/hashes and no remaining live imports/commands for retired
  files. Run focused checks for seeded variation, conservation, purchase boundaries,
  causal predictions, sparse/zero/invalid histories and unchanged scoring rules.
- Run 180/365-day headless examples at all three levels; inspect both graphs and
  error exports. Exercise native GUI playback, 0.5-second timing and slider reset.
- Check Git/build exclusions, unchanged production files and diff whitespace.

## Out of scope

- Missed-top-up/outage controls, manual entry UI, extra graphs, ML/segmentation,
  application/API/DB changes, runtime dependencies, hardware/OCR, siblings,
  commits and pushes. Stop for review after this research-only change.
