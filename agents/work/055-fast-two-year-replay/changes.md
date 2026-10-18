# Task 055: Fast two-year replay

The user requested direct implementation on 2026-10-18 and explicitly waived
the prompt/approval step for this task. No prompt was created.

## Recovery recorded before deletion

The requested removal is only
software/backend/research/forecasting/simulator_checks.py. Reference inspection
found documentation mentions but no runtime import. Its untracked contents are
not recoverable from Git, so an exact local copy was verified before removal:

- Recovery: .tmp/task055/simulator_checks.py (ignored, 26,152 bytes).
- SHA-256: 98A5BDC19B19C5934C8A2E8713E891DF2D17C90A582114C70D8A8D2A058450A7.
- Restore by copying this file back to the original path after checking the hash;
  this ignored local backup is not available in a fresh clone.
- The pre-change main is retained at .tmp/task055/simulator-before.py.

Earlier work/results, outputs, dependencies and other source files are retained.

## Changes and reuse

- Replay and household generation default to 730 days. The GUI timer defaults
  to 100 ms per simulated day, previously 500 ms; rendering adds overhead.
  Duration and speed retain their existing CLI overrides.
- Both existing graphs shade the selected 60/90-day lookback orange, from
  max(start, now - lookback) to now. The span is rebuilt by the existing draw
  path each update, moving forward with time without adding graphs or controls.
  The whole revealed history remains visible outside the highlighted window.
- This is two years of replay with repeated next-30-day predictions, not a
  two-year-ahead forecast. The model, calibration, monthly requirement, scoring
  and no-future-purchases assumption are unchanged.
- Removed only the requested check script after the recovery record above.
  Updated current README/context defaults and removed obsolete check commands;
  earlier work records and their historical checks/results remain intact.
- Main-source comparison against the retained pre-change copy is 6 additions
  and 3 deletions, below the 100-line implementation limit. Removed tests and
  documentation are excluded from that count.

## Verification actually run

- Default headless export (no --days override) completed all three randomness
  levels at 730 days/90-day lookback in out/task055-730-90/. All three PNGs
  decoded; the Mid image was visually inspected for the orange context band.
  Each level has 24 monthly snapshots, 23 matured horizons and one pending.
- An explicit 180-day/90-day export to out/task055-180-90/ reproduced all eight
  Task 054 JSON/CSV reports byte-for-byte, including the training manifest and
  summaries. Only the displayed window/default replay settings changed; this
  is not evidence of improved forecast accuracy or approval for integration.
- Python compilation and tracked-file whitespace checks passed. Production
  app/frontend/database/runtime diffs remain empty. No dependencies, services,
  database contents, sibling repositories, commits or pushes changed.
- Native TkAgg smoke checks passed with the 100 ms timer, Play/Pause, immediate
  monthly estimates, Reset and all slider levels. There are still two data
  graphs and three control axes. Both orange spans were checked at days 180
  and 700 with 60- and 90-day lookbacks: endpoints move with now, stop at now
  and never extend before the start. Future dotted curves still cover 30 days.
  The owned-window/day-700 image was visually inspected. Temporary evidence
  remains ignored under .tmp/task055/. The owned window, timer and figures
  closed; the helper exited zero. The removed suite was not rerun or replaced
  with a permanent test file.

## Local run

From software/backend/research/forecasting/:

```powershell
.\.venv\Scripts\python.exe simulator.py
```

Next work number is 056. The prompt waiver does not change the normal workflow
for later tasks. No automatic follow-on work or app integration.
