# Task 039: Minimal navigation and consistent typography

## Result

Completed approved Ticket 62 in 39 changed implementation lines. Tasks 037–038
are preserved. Subsequent Git handoff is recorded in Task 041.

- Removed the logo, Roventics Monitor name and Admin badge from navigation;
  retained the logo asset. Signed-out pages have no empty navigation bar.
- Shortened Back to meters to Back, left-aligned opposite email/account controls.
  Enlarged the account icon to a verified 28px; retained the full-email dropdown
  and distinct black Logout action.
- Centralised typography in the existing MUI theme: Arial/sans-serif, 16px body,
  captions/labels/buttons and 20–22px headings/forecast values. Rem-based sizes
  retain browser text scaling. Small/large button text is also 16px.
- Vertically centred meter name/owner on desktop; retained left-aligned stacking
  on phones. Updated roadmap, context and software/frontend READMEs.

## Reuse

- Existing Navigation, MeterWorkspace, MUI theme and typography variants.
- Existing Task 034 browser/CDP/Mailpit and exact-auth-fixture cleanup helpers.
  Read existing Task 038 demo meters without altering their histories.

## Verification

- PASS: Eight grouped live browser/API checks, including exact temporary cleanup.
  Desktop 1200px and phone 390px/320px layouts have no horizontal overflow.
- PASS: Back/account centre alignment and far-right account positioning;
  computed account icon is 28px, body/Back text 16px and heading/values 22px.
  Main typography uses the same font family and stays in the 16–22px range.
- PASS: Desktop name/owner vertical centres match; phone labels stack with the
  same left edge. Screenshots inspected under ignored `.tmp/task039/`.
- PASS: Full-email dropdown, distinct black Logout icon, short Back navigation,
  second-meter selection, Refresh and record/cancel. Logout revokes sessions.
- PASS: Configured admin still sees both demo profiles in All meters/search,
  with no role badge; admin phone layouts fit. Logo asset remains HTTP 200.
- PASS: Before/after comparisons show both demo balances/top-ups unchanged.
  No ledger writes, reminder calls, duplicate-key warnings or browser errors.
- PASS: Frontend suite: 30 checks across four files. Final TypeScript/Vite asset
  build exited zero; `git diff --check` passed (normal LF/CRLF notices only).
- The first live check found the icon still rendering at 20px despite its CSS
  override. Set the SVG size explicitly; final live check verified 28px.
- Removed only disposable auth test users/challenges, this run's captured emails
  and the exact temporary admin session. These fixtures can be recreated;
  retained demo meters/ledgers, real data and volumes were untouched.

## Boundaries

No backend, permission, route, model, dependency, database schema or demo-history
changes. Future app identity work remains Ticket 58; no new branding was added.
