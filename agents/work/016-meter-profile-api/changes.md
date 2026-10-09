# Task 016: Meter profile API and administration

## Result

Authenticated users can create, list, view, rename and delete nickname-only
meters. Normal users are restricted to their own meters; configured admin
emails receive unrestricted access to existing meters.

## API and access

- Added session-authenticated `/api/meters` list/create and
  `/api/meters/{id}` get/rename/delete routes.
- Extracted a reusable cookie-session dependency and added `is_admin` to the
  safe login and `/api/me` responses.
- Derived admin status from normalized comma-separated
  `MONITOR_ADMIN_EMAILS`; no role table or new service was introduced.
- Admins can manage every existing meter, while creation stays name-only and
  creates a meter for the signed-in user.
- Missing and inaccessible UUIDs both return the same 404. Duplicate names
  return 409, and invalid names return 422.
- Expanded credentialed development CORS to the required CRUD methods.

## Configuration

- Created ignored `software/.env` as the complete local Compose configuration
  source and set the approved personal admin email there.
- Synchronized committed examples with a non-personal admin address and useful
  Mailpit values.
- Removed Compose's duplicate inline defaults and added clear required-variable
  messages. Application defaults remain only for direct execution and tests.
- Confirmed Git ignores the local `.env`; the personal email does not occur in
  tracked content.

## Reuse

- Reused opaque cookie sessions, normalized email conventions, FastAPI settings
  injection, Task 015 raw-SQL repository operations and current API test style.

## Verification

- Focused settings/auth/meter/CORS tests: 17 passed.
- Full backend suite: 39 passed.
- `docker compose config --quiet` passed with the real local `.env`.
- An intentionally incomplete temporary env failed clearly with
  `FRONTEND_PORT is missing a value`; the temporary file was removed afterward.
- Integration coverage confirms normal-user isolation and administrator
  list/rename/delete access.
- `git diff --check` passed with only line-ending notices.
- `refocus.md` remained absent after the Task 015 workspace notice and was not
  recreated, modified or included.
