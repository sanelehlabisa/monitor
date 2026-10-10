# Task 032: Server-driven meter search

## Result

Users can search accessible meter profiles by keyword, and administrators can
also find profiles from a partial owner email.

## Change and reuse

- Extended the existing raw-SQL list query with an optional case-insensitive
  literal substring match across meter name and owner email.
- Added bounded optional `q` input to `GET /api/meters` while retaining the
  established regular-user/admin ownership scope and stable result ordering.
- Updated the typed frontend client to encode the keyword and added a compact
  Material UI Search/Clear form with loading, request-error and no-match states.
- Active search is cleared after meter creation and the authoritative server
  list is reloaded so the new profile remains visible.
- Reused Task 031 `My meters`/`All meters`; no client-side keyword filtering,
  schema change or new dependency was introduced.

## Verification

- Focused live-PostgreSQL repository/API checks: `3 passed`.
- Complete backend suite: `60 passed`.
- Frontend tests: `21 passed`.
- Frontend production build: passed.
- Frontend-proxy owner-name search, owner isolation and admin partial-owner-email
  search: passed; synthetic user, meter, OTP and Mailpit data were removed.
- `git diff --check`: passed (line-ending conversion warnings only).
