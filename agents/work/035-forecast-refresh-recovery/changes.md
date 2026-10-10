# Task 035: Forecast refresh and recovery

## Results

- Completed Ticket 59: added an icon-labelled Refresh action above the planning
  summary, disabled while loading or saving. No timer or client calculation.
- Unified initial/manual/post-save dashboard reads through loadDashboard.
  Loading clears estimates; failure ends loading and displays explicit retry
  guidance while retaining the available ledger records.
- Successful writes remain successful even when their dashboard reload fails.
  The form clears, the saved record remains visible and Refresh retries only GET.
- Added a navigation version guard to discard older dashboard responses after
  leaving/reopening a meter or signing out. Saved-write responses also check the
  version before applying records or starting a dashboard read.
- Updated the roadmap, context and software/frontend READMEs. Household
  validation, deployment and the supplied-logo ticket remain separate.
- Implementation totals 85 changed lines (68 added, 17 removed); no backend,
  database, dependency or forecast formula changes.

## Reuse

- Extended getDashboard/applyDashboard and the existing ledger mutation flow.
- Reused ForecastPanel, MUI Button and the installed Refresh icon.
- Reused Task 034's isolated Edge/CDP driver, Mailpit OTP flow and exact raw-SQL
  fixture cleanup. Task-specific browser fault injection affected dashboard
  reads only; authentication, writes and successful reads used the real stack.
- Temporary scripts/results remain under ignored .tmp/task035; no new testing
  dependency or permanent demo data was introduced.

## Verification

- PASS: 22 existing/updated frontend checks, including unavailable-versus-loading
  rendering; TypeScript and Vite production build.
- PASS: real browser email OTP sign-in with the HTTP-only cookie.
- PASS: failed initial dashboard read has an enabled retry action and no endless
  spinner; Refresh recovers the expected 4 kWh/day forecast.
- PASS: manual refresh performs one GET and no writes, disables Refresh while
  pending and updates the backend calculation timestamp.
- PASS: failed manual refresh hides planning numbers, retains 100/80 kWh actual
  records and clears the error on successful retry.
- PASS: saved balance and saved top-up each survive a failed post-save read;
  forms clear, the saved message appears and retry adds no duplicate records.
- PASS: held old-meter response cannot replace another meter's insufficient-data
  state or an updated forecast after reopening the same meter.
- PASS: sign-out invalidates a pending dashboard response and /api/me returns
  401. Zero uncaught browser errors across nine grouped live checks.
- PASS: exact synthetic users, OTP challenges, cascading records/sessions and
  captured Mailpit messages removed; cleanup reports zero remaining fixture users
  or OTPs. Existing household data and unrelated email captures were preserved.
- PASS: git diff --check.
