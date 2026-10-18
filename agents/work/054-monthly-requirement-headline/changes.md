# Task 054: Monthly requirement headline

Approved and implemented on 2026-10-18. Research only; no commit or push.

## Changes and reuse

- The GUI now displays "Predicted monthly requirement (30 days)" using the
  existing consumption_30 = estimated daily usage x 30. This is full predicted
  consumption, independent of the balance, not an extra-purchase amount.
- Launch, Reset and a changed randomness level explicitly record the known
  configured starting balance through the existing record_balance method before
  rendering. The initial 300 kWh reading enables an immediate, labelled assumed
  estimate: approximately 301.4 kWh/month at the frozen 10.045816 kWh/day prior.
  No earlier readings are invented; replay does not duplicate the starting fact.
- The requirement follows new usage evidence without artificial smoothing or a
  forced minimum. Genuine zero use remains zero; empty or invalid histories do
  not acquire invented estimates.
- Reused existing consumption_30, recording/deduplication, render and reset paths.
  Forecasting, training calibration, additional-purchase calculation and exports
  remain unchanged. No new dependency, control, model or production default.
- Updated the forecasting/backend READMEs and agents/context.md. Task 053's
  numerical evidence remains historical and its limitations/adoption gates stay
  open. This display change establishes no forecasting accuracy improvement.

## Verification actually run

- All 23 focused checks passed independently and in the root rerun. Three added
  checks cover purchase-independent monthly usage, updates from new readings and
  a known starting balance without duplicate replay. Existing empty/zero/invalid,
  UTC, rolling-window, conservation and causal-scoring checks still pass.
- At 15 kWh/day, 300 kWh remaining gives 20 days, 450 kWh monthly requirement
  and 150 kWh extra needed. A known 300 kWh purchase one day later gives 585 kWh
  balance and zero extra needed, while monthly requirement remains 450 kWh.
  A separate changed-reading fixture updates the monthly estimate from 300 to
  450 kWh rather than holding it fixed.
- Native TkAgg verification passed: immediate labelled estimates before Play,
  actual 500 ms playback and Pause, no duplicate starting reading, Reset and all
  three slider levels. Resets retain exactly one known starting observation and
  its three unavailable pre-update score records, not an empty ledger. Bare
  Simulation still starts empty and unavailable. Zero and invalid GUI states
  also passed. The two graphs and existing controls are unchanged.
- Own-window and before/after-purchase captures were inspected. Temporary helper
  and evidence are ignored under .tmp/task054/; the owned window, timer and
  figures closed in finally and the helper exited successfully. The heading
  also fits the default 1200x850 canvas and 125% DPI without wrapping.
- Headless 180-day/90-day-lookback export passed at all three levels into
  out/task054-180-90/. All eight JSON/CSV reports are SHA-256 byte-identical to
  out/task053-180-90/ (manifest, summary and six CSVs), confirming unchanged
  headless model/scoring outputs. All three PNGs decoded. Existing results and
  the local environment were retained; no installation or Docker restart needed.
- Production app/frontend/database/runtime file diffs remain empty. Whitespace
  checks pass. Main implementation comparison against ignored
  .tmp/task054/simulator-before.py is 5 additions and 4 deletions (9 changed
  lines), below the 100-line limit; tests and documentation are excluded.

## Handoff

From software/backend/research/forecasting/:

```powershell
.\.venv\Scripts\python.exe simulator.py
```

Live application, API, database, siblings, model adoption and Git history are
unchanged. No files were retired in this task. Tasks 050-054 remain uncommitted.
Stop for review; next work number is 055 and requires the normal approval flow.
