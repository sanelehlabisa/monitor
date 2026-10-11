# Task 037: Simple planning dashboard

## Results

- Replaced four estimate tiles with a compact summary: estimated balance, days
  remaining with top-up-by date beneath, and monthly purchase kWh. The latter
  still means additional energy needed for the next 30 days, not total usage.
- Latest actual reading/time and calculation timestamp stay visible. Usage and
  interval assumptions sit inside closed Calculation details.
- Two large icon buttons reveal only the matching existing record form; Cancel
  writes nothing and a successful save clears/closes it. Write errors stay
  visible and successful writes followed by failed reads remain retryable.
- History and Meter settings start closed, preserving record tabs, correction,
  deletion, rename and existing confirmations. Reduced header duplication and
  moved Refresh below the primary content; long owner emails wrap on phones.
- Fixed a sibling-key collision discovered in the new settings wrapper during
  browser checks. Settings and dashboard now have distinct stable keys.
- Updated roadmap, context and component documentation. Implementation totals
  199 changed lines, within the approved 200-line exception; no backend, database,
  forecast math, dependency or branding asset changes. Subsequent Git handoff is
  recorded in Task 041.

## Reuse

- ForecastPanel, LedgerPanel, MeterWorkspace, existing MUI icons/styles and
  dashboard/save/retry handlers; existing UTC/local date helpers are unchanged.
- Native details/summary avoids extra state or dependencies for secondary panels.
- Reused Task 034's isolated Edge/CDP and scoped raw-SQL fixture cleanup tooling
  under ignored .tmp/task037/. No real user session or meter was used.
- Checked the key fix against [React's sibling-key guidance](https://react.dev/learn/rendering-lists).

## Verification

- PASS: all 22 frontend checks, including updated default-closed forms/details
  and monthly-recommendation assertions; production asset build and diff check.
- PASS: real local email OTP login; new-meter unavailable state; each entry form,
  cancel without writing, actual balance/top-up saves, automatic forecast refresh
  and unchanged UTC storage. Synthetic 100/20/80 kWh history derives 4 kWh/day,
  approximately 76 kWh remaining, 19 days and 44 additional kWh for 30 days.
- PASS: screenshots inspected at desktop 1200px and phones 390px/320px; no
  horizontal overflow, and phone record/cancel works.
- PASS: calculation/history expansion, balance correction/restoration, record
  tabs and meter rename. Hidden panels do not hide error/retry feedback.
- PASS: manual Refresh/recovery performs no writes, stale estimates disappear
  after failed reads, and a saved top-up followed by a failed estimate reload
  closes its form and survives retry without duplicate purchases.
- PASS: zero use has no fabricated date; inconsistent history withholds estimates.
  No reminder requests, uncaught browser errors or duplicate-key warnings.
- PASS: exact synthetic users, their meters/ledgers/sessions, OTPs and captured
  Mailpit emails cleaned up. Existing household data and volumes were not removed.
- Existing deletion handlers/confirmations are unchanged; this task's live checks
  concentrated on create, cancel, correction, rename and recovery. No new household
  trial, deployment or forecast-model validation is claimed.
