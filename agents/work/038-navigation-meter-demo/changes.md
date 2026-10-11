# Task 038: Navigation and linkable meter demo

## Result

Completed approved Ticket 61. Existing Task 037 work is preserved; no backend,
SQL schema, permission or forecast-model changes. Subsequent Git handoff is
recorded in Task 041.

- Added responsive navigation with the signed-in email/avatar at the far right,
  a full-email dropdown and black Sign out action using Logout rather than the
  Back arrow. Retained the admin indicator; moved Back to meters into navigation.
- Added `/meters/<uuid>` URL/state handling using browser history, without a
  dependency. Direct reload and login return open the authorised meter;
  Back/Forward, logout and confirmed deletion keep URL/workspace consistent.
  Invalid/inaccessible links recover without exposing foreign records. Failed
  same-URL opens can be retried; navigation invalidates older dashboard reads.
- Widened the signed-in container and separated name/owner details above the
  planning card. Existing entry forms, history and settings remain on demand.
- Created and retained a separate local `monitor-demo@example.test` user with
  Demo Home and Demo Shop through real OTP/Mailpit and existing meter/ledger APIs.
  Each has two balances and one intervening top-up, giving real deterministic
  forecasts at 4 and 8 kWh/day. Initial estimates were approximately 76/112 kWh,
  19/14 days and 44/128 additional kWh for the next 30 days. No UI values are
  fabricated; real empty meters still show Not enough data.
- Reran setup: both demo meters were reused with no duplicate records or history
  overwrite. No startup seeder or demo endpoint was added. Admin access remains
  through All meters and owner-email search, with existing full management.
- Updated root roadmap, context and software/frontend READMEs, including retained
  demo access and separate disposable walkthrough instructions.

## Reuse

- Existing React/Material UI theme, icons, auth/cookie APIs and brand asset.
- Existing meter selection, guarded shared dashboard loader, record save flows,
  admin views/search and UTC/local date helpers.
- Existing Task 034 headless Edge/CDP, Mailpit and scoped raw-SQL fixture tools.
  Temporary Task 038 harness/artifacts remain ignored under `.tmp/task038/`.

## Verification

- PASS: 12 grouped live browser/API checks, including exact disposable cleanup.
  Real email OTP/cookie login, account dropdown/logout, direct meter reload,
  browser Back/Forward, anonymous/owned login return and deletion-to-home URL.
- PASS: Invalid/missing/foreign IDs with no disclosed foreign meter content;
  second regular user cannot read or write demo meters. Configured admin can
  search/open both demos and sees management controls; an admin rename on a
  disposable foreign meter also succeeded.
- PASS: Delayed dashboard responses cannot restore a departed meter; failed
  same-URL meter opening can be retried. Real balance/top-up forms save/close,
  refresh numerical estimates and preserve UTC storage.
- PASS: 1200px desktop and 390px/320px phone layouts, dropdown full-email display,
  black Logout icon and same-row Back/account alignment with no overflow. Admin
  home also checked at both phone widths. Screenshots inspected locally.
- PASS: Both retained demo forecasts, raw UTC balance records and repeat setup
  without duplicate creation. No reminder calls, duplicate-key warnings or
  uncaught browser errors.
- PASS: `docker compose -f dev.docker-compose.yaml exec -T frontend npm test`:
  30 checks across four files. Production asset build (`npm run build`): TypeScript
  and Vite passed. `git diff --check` passed (normal LF/CRLF notices only).
- Initial checks caught a narrow-phone wrapping issue, fixed with responsive
  grid tracks. A repeated-login harness failure selected an already-used Mailpit
  message; the harness now excludes consumed messages. Final run exited zero.
- Removed only disposable synthetic users/challenges/ledgers, their captured
  emails and the exact temporary admin session. Those test fixtures can be
  recreated; retained demo meters, real users/records and volumes are untouched.
- 231 changed implementation lines relative to the Task 038 start snapshot,
  including new navigation/URL modules; within the approved 250-line exception.

## Handoff

Refresh the app, sign in as your configured admin, choose All meters and search
`monitor-demo@example.test`. Demo Home and Demo Shop are ready for manual testing.
Estimates change with time; Refresh recalculates without adding records.
