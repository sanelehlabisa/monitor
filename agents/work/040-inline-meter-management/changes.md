# Task 040: Inline meter management

## Result

Completed approved Ticket 63 in 154 changed implementation lines, within the
approved 200-line exception. Preserved Tasks 037–039. Subsequent Git handoff is
recorded in Task 041.

- Increased the account SVG from 28px to 42px while preserving right alignment.
- Replaced selected-meter headings/settings with aligned Name/Owner key-value
  rows. Name remains editable with a pencil-only save action or Enter; Owner
  remains read-only. Removed the bottom Meter settings section.
- Added separate pencil/trash actions to each meter-list row, without nested
  buttons or accidental navigation. Pencil opens an inline editor; pencil/Enter
  saves and Escape cancels. Blank/unchanged saves are disabled.
- Generalised existing rename/delete handlers to accept the target meter.
  Confirmation names it and warns that associated balance/top-up records will
  be deleted. Rename failures retain drafts; deletion failures retain rows.
- Kept rows mounted during saves and disabled conflicting navigation, meter and
  ledger actions. Renaming under search repeats the existing backend query.
- Updated root roadmap, context and software/frontend READMEs.

## Reuse

- Existing MeterWorkspace, Navigation, MUI components/icons and name limits.
- Existing authenticated meter APIs, error messages, confirmation and workspace
  clearing; no new backend route, schema, dependency or forecast logic.
- Task 034 local Edge/CDP, OTP/Mailpit and exact-fixture cleanup helpers. Task 039
  browser-driver pattern; new temporary scenarios live under ignored .tmp/task040.

## Verification

- PASS: 12 grouped live browser/API checks, including exact disposable cleanup.
- PASS: Desktop 1200px and phone 390px/320px list/details layouts; computed 42px
  account icon, right alignment, aligned keys/actions and no horizontal overflow
  or nested buttons. Screenshots inspected.
- PASS: Row edit without navigation, Escape cancellation, blank save disabled,
  real duplicate-name error, Enter/pencil save and pending-action protection.
- PASS: Named delete cancellation sends no request; simulated failed rename/delete
  preserves the draft/row and enables retry. Confirmed owner/admin deletions work.
- PASS: Selected-meter rename, URL reload and Back retain the saved name. Another
  regular user cannot list/read/rename/delete the disposable owner's meter.
- PASS: Admin All meters/email search provides full row actions; renaming under
  name search re-queries the server and removes a now-unmatched result.
- PASS: Retained Demo Home/Shop forecasts, record/cancel and Refresh still work.
  Before/after ledger snapshots match; no ledger writes, reminder requests,
  duplicate-key warnings or browser exceptions.
- PASS: All 30 frontend checks across four files; TypeScript/Vite asset build
  and git diff --check. Normal Windows LF/CRLF notices only.
- Initial checks caught an unavailable DeleteOutline import; replaced it with
  the installed DeleteOutlined icon. Temporary browser-helper variable, cold-load
  timeout and reload synchronisation issues were corrected before the passing run.
- Removed only disposable test meters/users/challenges, captured test emails and
  the exact temporary admin session. These fixtures are reproducible; retained
  demos, real records and volumes were not removed. Isolated browser closed.

## Boundaries

No backend/schema, permissions, forecast, route, dependency, branding, deployment
or sibling-repository changes. No edits to refocus.md.
