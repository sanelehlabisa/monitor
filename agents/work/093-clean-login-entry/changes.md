# Task 093 changes

- Home now has one Log in button. `/login` offers email login or guest use;
  selecting email reveals the existing email/code form. Back returns through the
  choice page/home. Initial session lookup does not block these public actions.
- Removed routine browser-storage paragraph/row and email login's unnecessary
  explanatory sentence. Real storage failure/corruption/retry warnings remain.
- Reused existing route state, LoginPage, Navigation and the guest panels.
  Protected links keep their route; signed-in users keep account navigation.
- Successful manual login invalidates a late session-restore response, so a slow
  initial request cannot undo verification or leave the account screen loading.
  No authentication policy, session duration, data or backend behavior changed.
- Updated context/README guidance. Account saving remains 68.4; remembered login
  remains 68.6. Prior Task 092 records describe its original entry presentation.

Verification: TypeScript/Vite build and all 44 existing checks pass. Updated one
existing homepage assertion for the new single-action UI; no test files added.
Four owned browser groups with synthetic APIs verify route choices, email/code
login before pending session restore completes, stale-response protection, Back,
guest-data retention, no routine copy, protected links, real failure warnings and
1280/390/320px guest layouts. No browser runtime exceptions. Evidence is under
ignored `.tmp/task093/`; owned browser/server close after verification.

No live services/data, dependencies, database, deployment, commits or pushes changed.
