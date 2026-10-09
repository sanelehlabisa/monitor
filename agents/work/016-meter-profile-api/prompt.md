# Task 016: Meter profile API and administration

## Aim

Expose authenticated meter CRUD so users manage their own meters and configured
administrators manage every user's meters.

## Clarifications

- Question: How are administrators configured? Answer: Use normalized emails
  from comma-separated `MONITOR_ADMIN_EMAILS`; the local ignored `.env` contains
  the user-approved address, while committed files use a safe placeholder.
- Question: What may an administrator do? Answer: List, view, rename, and delete
  every existing meter, as well as create their own meters. Regular users have
  the same operations only for meters they own.
- Question: What data is needed to add a meter? Answer: Only its name. Creating
  a meter on behalf of another user is not needed by the simple V1 flow.

## Change

- Parse and normalize `MONITOR_ADMIN_EMAILS` as a small settings list and pass it
  through development Compose without introducing roles or another service.
- Create the ignored `software/.env` with the complete local development values,
  including the approved local admin, and keep `.env.example` synchronized with
  a non-personal administrator example.
- Remove duplicated fallback values from Compose interpolation so development
  configuration comes from the visible `.env` file instead of being hidden in
  both Compose and settings. Retain only necessary application-level defaults
  that are covered by settings tests.
- Add a reusable cookie-session authentication dependency and expose `is_admin`
  from `/api/me` without exposing secrets.
- Add authenticated list, create, retrieve, rename, and delete meter endpoints.
- Return all meters with owner identity to administrators; scope every regular
  request to the authenticated owner and use a generic not-found response for
  inaccessible IDs.
- Return clear validation and duplicate-name conflicts, and permit PATCH/DELETE
  in development CORS.
- Cover unauthenticated access, normal-user isolation, and administrator access
  with API tests; update backend/config documentation and changes.md.

## Reuse

- Reuse `monitor_session`, `authenticate_session`, `normalize_email`, current
  response models, settings injection, and the Task 015 repository.

## Verify

- Run focused API/settings tests, then the full backend suite in Compose.
- Exercise normal and administrator HTTP flows through the running stack.
- Confirm the personal email is ignored by Git and absent from tracked diffs.
- Confirm resolved Compose configuration uses the `.env` values and reports
  missing required values clearly.
- Run `git diff --check`.

## Out of scope

- Acting as another user when creating a meter, frontend UI, ledger entries,
  forecasts, persisted role tables, invite flows, and production authorization.
