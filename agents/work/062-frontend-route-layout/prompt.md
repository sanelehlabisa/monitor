# Task 062: Frontend route layout

## Aim

Organize frontend screens and their components around the existing routes.

## Clarifications

- Keep React/Material UI, URLs, appearance and behavior unchanged. Login remains
  the existing unauthenticated view, not a newly introduced /login URL.
- Run after Task 060; preserve Task 061 and all pending Task 059 changes.

## Change

- Add routes/login/LoginPage and routes/meters/MetersPage/MeterDetailsPage, with
  meter-only components and routing helpers under routes/meters/.
- Split the mixed AuthPanels/MeterWorkspace files only as needed. Put shared
  Navigation in components/ and API/date/time/theme helpers in lib/; colocate
  relevant tests. Delete superseded files rather than adding re-export shims.
- Keep coordinated auth, pathname/history, request-version guards and CRUD state
  in App; retain component keys, form reset, login return and stale-reply behavior.
  No new router, store, context, hooks framework or duplicate API layer.
- Update guidance/context and changes.md. Line-budget exception covers file moves
  and extraction of existing screens/theme, not a redesign or feature additions.

## Reuse

- Existing components, manual route helper, API client, theme and checks.

## Verify

- Confirm source app services remain stopped before moving bind-mounted code;
  if unexpectedly running, ask before changing their state or moving code.
- Run frontend tests and TypeScript/Vite build; retain existing assertions.
  Run focused mocked-browser checks for login/return, direct meter URLs,
  Back/Forward, My/All/search, rename, ledger forms/refresh/logout and phone layout.
  Record actual results/limits, stale imports, links and whitespace; clean only
  task-owned verification resources. No source data or app-service changes.

## Out of scope

- UI/theme/route/API/model changes, dependencies, real email, live DB writes,
  production deployment, source restarts, research/history deletion, commits/pushes.
