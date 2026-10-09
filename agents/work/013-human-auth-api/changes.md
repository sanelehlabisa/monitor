# Task 013: Human authentication API

## Result

Ticket 45 is complete. A valid email can request a Mailpit-delivered OTP, verify
it to create or reuse a user, receive an opaque cookie session, access `/api/me`
and revoke that session through logout. The Material UI login flow remains
Ticket 46.

## API and cookie boundary

- Added `POST /api/auth/request-otp`, `POST /api/auth/verify-otp`,
  `POST /api/auth/logout` and `GET /api/me` in one focused router.
- Normalized email input and applied practical email-length/shape and six-digit
  code validation without another package.
- Returned the same HTTP 202 body for delivery success, request-rate rejection
  and expected SMTP failure while leaving unexpected server failures visible.
- Returned generic HTTP 401 responses for OTP and session failures without
  exposing internal policy state.
- Set `monitor_session` with HttpOnly, SameSite Lax, path `/`, a 30-day maximum
  age and Secure outside local development. Response JSON contains only user ID
  and normalized email.
- Logout revokes only the presented session, clears its cookie and remains
  idempotent when no usable cookie exists.
- Enabled credentialed CORS for GET/POST from only the configured frontend
  origin and retained the content-type header allow-list.

## Reuse

- Reused Task 010 verification/user creation, Task 011 OTP email delivery and
  Task 012 session creation, authentication and revocation.
- Reused the application factory, typed settings and direct Psycopg connector.
- Used existing FastAPI/Pydantic capabilities; no dependency, session secret or
  environment variable was added.
- Implementation exceeds the 100-line aim because the complete four-route
  cookie and error-translation boundary was kept together and tested as one
  vertical authentication slice.

## Verification

- Full backend suite: 35 tests passed.
- A live PostgreSQL/Mailpit flow requested a code for a new email, read the code
  from Mailpit, verified it, authenticated `/api/me`, logged out and then
  received HTTP 401.
- Tests confirm identical request responses for success, rate limits and SMTP
  failure; unexpected failures remain HTTP 500.
- Tests confirm validation, generic verification failure, idempotent logout,
  cookie flags, no credential JSON and configured-origin credentialed CORS.
- Integration-test cleanup left zero sessions, users and OTP challenges.
- `docker compose config --quiet`, Python compilation and `git diff --check`
  passed.
- Temporary containers and their network were removed after verification; the
  PostgreSQL and frontend dependency volumes were preserved.
- `refocus.md` retained SHA-256
  `8EE807DBC69F88F225D93D608DA7A5537FF2745454109F659342521B90849257`,
  remained untracked and was excluded from the commit.
