# Task 032: Server-driven meter search

## Aim

Let users quickly find accessible meter profiles through a minimal keyword query
handled primarily by the backend.

## Clarifications

- Question: Where is search performed? Answer: The frontend sends a keyword to
  `GET /api/meters?q=...`; PostgreSQL performs the filtering through raw SQL.
- Question: Which fields are searched? Answer: Case-insensitive substring search
  across meter name and owner email.
- Question: What authorization applies? Answer: Apply the existing owner/admin
  scope before returning results; regular users can never discover another
  user's meter, while admins may search every accessible owner email.
- Question: How should the frontend behave? Answer: Provide one compact search
  field with explicit Search and Clear actions and render the API response. Keep
  the Task 031 `My meters`/`All meters` presentation.
- Question: Are counts required? Answer: Keep this ticket minimal; do not add a
  separate count contract or aggregation endpoint.

## Change

- Extend the raw-SQL meter list function with an optional escaped keyword while
  preserving stable name ordering and owner scope.
- Add an optional bounded `q` parameter to `GET /api/meters`; omitted or
  whitespace-only values retain the current complete accessible list.
- Update the typed frontend client to encode the query and add a small MUI
  Search/Clear form with loading, no-match and request-error feedback.
- Clear an active search after creating a meter and reload the authoritative
  list so the new admin/user-owned profile is immediately visible.
- Update focused repository/API/frontend coverage and nearby documentation.

## Reuse

- Reuse `list_meters`, `meter_owner_scope`, the cookie-authenticated API helper,
  Task 031 admin views and existing Material UI form/error patterns.

## Verify

- Run focused live-PostgreSQL repository/API checks plus the complete backend
  suite.
- Run frontend tests and production build.
- Through the development frontend proxy, confirm a regular user searches only
  owned names and an admin finds profiles by partial owner email.
- Run `git diff --check`.

## Out of scope

- Client-side keyword filtering, pagination, ranking, fuzzy search, new indexes,
  user management, create-on-behalf, physical devices, hardware, OCR and ML.
