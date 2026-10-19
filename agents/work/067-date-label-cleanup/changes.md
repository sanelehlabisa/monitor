# Task 067: Date Label Cleanup

## Status

Approved by the user with "i approve 067". The wording change is implemented;
frontend verification passed. All uncommitted Task 066 code/tests/docs
are preserved. The user subsequently authorized committing/pushing completed
Tasks 066–067 to master; earlier no-commit notes describe completion-time scope.

## Inspection and reuse

- Read agent instructions/context/rules/template and relevant frontend/backend/
  software README sections. The visible suffix is literal text in ForecastPanel;
  the existing utcDateDisplay helper must remain to avoid a previous-day shift.
- App.test.tsx currently asserts the suffix. The requested change is that label
  and assertion only, plus factual documentation/results; no date/math change.
- Independent read-only deployment/status review confirms run_forecast_model is
  implemented and covered by Task 066's isolated/mocked checks. The research
  candidate is not integrated, and the current app has no automatic scheduler.
- Production Docker targets/Nginx exist; production Compose/runtime environment,
  real SMTP, public HTTPS, data/backup/restore operations and live release checks
  remain. New forecasting research and email styling are not technical minimum
  prerequisites for a small pilot; the existing roadmap is not reordered here.

## Implementation

- Removed only the literal " (UTC)" suffix from ForecastPanel's monthly-date label.
- Inverted the matching markup assertion to require its absence. UTC calendar
  formatter/previous-day protection and forecasting/rollover code are unchanged.
- Updated current frontend README/context. One runtime-line replacement only;
  no API, backend, calculation, layout, dependency or service change in this task.
- Read-only served-module check confirms Vite's hot-reloaded panel contains the
  monthly label without the suffix. No live meter/customer data or session used.

## Preparation checks and limits

Preparation made no application edits, source data/service/mail actions or Git
writes. Task 066's backend/browser results remain historical evidence; Task 067
does not rerun or claim them. Fresh frontend results are recorded below.

## Verification

- All 43 frontend checks in four files passed in 24.29s. This includes the markup
  assertion for no suffix, the unchanged UTC-formatted date and western-timezone
  previous-day protection.
- TypeScript and Vite production build passed (931 modules, Vite 4.05s). The
  pre-existing >500 kB chunk warning remains. All 12 package/lock/installed pins
  match; no dependency or host node_modules changes.
- Used the existing pinned frontend image in one task-owned network-none
  container with read-only source mounts. Exact identity/label/mount checks
  preceded removing only that container; ignored build/evidence files remain.
  Evidence: .tmp/task067/build-result.json and
  build-71885197-027/{build.log,result.json,cleanup.json}.
- Whitespace checks and the read-only Vite served-module check pass. No browser
  replay, backend test run, live record/session/email action, source service
  restart/rebuild or Git handoff was needed or performed.
