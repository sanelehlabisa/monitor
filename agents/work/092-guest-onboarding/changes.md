# Task 092 changes

Implemented the approved first usable guest slice (68.1–68.3). Homepage entry and
`/guest` work without email login or successful session lookup. One named local
meter supports balance/top-up add/edit/delete, rename, forecasts, reload and clear.
Existing account routes use their existing APIs; restored users redirect to them.

## Reuse and behavior

- Reused MeterDetailsPage, ForecastPanel, LedgerPanel, API/domain shapes and date
  helpers. Added a guest route, local document helper and forecast function.
- `monitor.guest.v1` stores validated domain records, never credentials/account
  records. No guest history is sent to APIs. Clear requires confirmation.
- Integer thousandths/millionths mirror Python energy/rate rounding and UTC month
  rules without floating energy arithmetic or a new dependency. Focus/resume,
  minute ticks and record changes recalculate the forecast.
- Failed persistence keeps visible in-memory records with warning/Retry save;
  corrupt data is not overwritten. Detected other-tab changes block stale saves.
  Simultaneous multi-tab writes are not a supported synchronization mechanism.
- Account history save (68.4) and three-day remembered login (68.6) remain planned.
  Guest Back returns to ordinary login; no misleading save-to-account action is
  added before that feature is implemented.

## Actual verification

- TypeScript/Vite production build and all 44 existing frontend checks pass.
  An existing check caught a signed-out Back regression; explicit guest navigation
  scope fixes it. No test files or dependencies added.
- 215 vectors from the unchanged Python model match browser outputs for default,
  measured, zero, depleted and inconsistent histories, top-up boundaries, irregular
  times, rounding and calendar/year boundaries. Run-out times agree within 1 ms.
- Local helper checks cover CRUD/validation, reload, blocked/corrupt storage and
  compare-before-write conflicts. Nine owned headless-browser groups pass with
  synthetic API fixtures: guest entry during pending/failed session lookup,
  record CRUD/recalculation, reload, 1280/390/320px layout, full/blocked/corrupt
  storage/retry, stale-tab protection, returning admin list/detail and protected
  deep links. Guest requests are session reads only; no ledger uploads.
- Visually inspected the 390px screenshot. No runtime exceptions or horizontal
  overflow at checked widths. Evidence is in ignored `.tmp/task092/`; no live API,
  SMTP, private records or source services used. Owned browser/server were closed.
- Local node_modules had missing icon files/types. Restored 24 missing files from
  the integrity-verified existing locked package cache; no manifest/lock/version
  changes. Stopped partial isolated install/pack attempts.
- Vite reports a non-fatal single-bundle size warning (~538 kB); no unrelated
  code-splitting work added. Tests/build were rerun after the navigation fix.

No files deleted, database/services changed, application deployed, commits or
pushes made for this task. Earlier planning was published as 504ac1c.
