# Task 092: First usable guest onboarding

## Outcome
Let someone use Monitor's core estimates and save one meter's records in this
browser without email login. Covers the first usable slice of 68.1–68.3.

## Questions and answers
- Guest records persist locally without login; authenticated data uses the backend.
- Homepage offers Use without logging in. Guest workspace offers Log in and save
  to account; its verified-login history save is the following 68.4 slice.
- Remembered login is confirmed three days, implemented separately under 68.6.
- No unresolved product questions for this slice; no schema/index changes needed.

## Scope and reuse
- Add a public `/guest` entry and the homepage action. Session lookup failure or
  delay must not prevent guest entry; keep account meter deep links protected.
- Reuse ForecastPanel, LedgerPanel, current meter presentation and date helpers.
  Keep the current Material UI theme and avoid a second dashboard design.
- Add small typed local meter/ledger functions using the existing domain shapes,
  with validated, versioned browser storage. Start with one guest meter: name,
  balances and top-ups, including add/edit/delete and immediate recalculation.
  Keep the boundary compatible with existing API operations; no storage framework.
- Implement the current forecast locally in one function, using the Python model
  as reference: labelled 10 kWh/day from one balance, measured valid intervals,
  honest unavailable states, existing rounding and UTC calendar-month rules.
- Handle reload/resume, clear confirmation and unavailable/full/corrupt storage.
  Show whether data was saved; retain useful unsaved input on failure. Explain
  local storage limits briefly. Do not send guest history to APIs or analytics.
- Preserve existing email/account/admin/shared-meter flows. Keep account records
  and credentials out of the guest store. Signed-in users use account routes;
  normal login/logout must not import, merge or copy records implicitly.

## Verification
Run the frontend build and relevant existing checks; add no test files. Compare
local results with current Python outputs for default/measured/invalid histories,
top-ups, zero use, rounding and month boundaries. Verify desktop/phone guest entry,
reload, record changes, storage failures and unchanged authenticated navigation
using an isolated walkthrough. Do not restart source services or alter live data.

## Exclusions
68.4 login-and-save/import/retry implementation; 68.6 session changes; database,
schema/index work; synchronization, mobile packaging, tracking, dependencies,
deployment, public posting, commits or pushes without further instruction.

## Approval
Approved by the user: execute Task 092 and keep it simple.
