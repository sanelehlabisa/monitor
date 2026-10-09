# Task 012: Session storage and policy

## Aim

Add a minimal raw-SQL session boundary that can turn a successfully verified
user into a secure, revocable 30-day login session without exposing HTTP routes
yet.

## Clarifications

- Question: How should sessions work across browsers and devices? Answer: Allow
  multiple independent sessions per user, each with a fixed 30-day expiry.
- Question: What credential should authenticate later backend requests? Answer:
  Use a cryptographically random opaque session token; never use the email or OTP
  as an API token.
- Question: How should the token be stored? Answer: Return plaintext only once for
  the future cookie layer and persist only its SHA-256 digest because the token
  has high random entropy.
- Question: What cookie and request behavior follows this task? Answer: Task 013
  will use `monitor_session`, `HttpOnly`, `SameSite=Lax`, `Secure` outside local
  development, generic OTP request responses and the approved four auth routes.
- Question: How is this kept small? Answer: Task 012 implements storage and
  policy only; Task 013 owns FastAPI routes, CORS credentials and cookies.
- Question: What happens to `refocus.md`? Answer: Leave it unchanged and
  untracked.

## Change

- Add forward-only migration `003_user_sessions.sql` with session UUID, owning
  user foreign key, unique SHA-256 token digest, creation/expiry and optional
  revocation timestamps.
- Add constraints for digest shape and expiry chronology plus indexes supporting
  token lookup and a user's sessions.
- Add a focused typed session module that creates a 32-byte URL-safe random
  token, stores only its digest, resolves a live token to its user and revokes
  the presented session.
- The implementation may modestly exceed the 100-line aim so the migration and
  create/authenticate/revoke invariants remain one cohesive security boundary.
- Use a fixed 30-day lifetime in reviewed code and allow multiple live sessions
  for different browsers/devices.
- Return one generic authentication-domain error for missing, expired, revoked
  or unknown tokens.
- Add unit tests for token generation/digests and PostgreSQL integration tests
  for creation, multiple devices, lookup, expiry, revocation and plaintext
  absence.
- Update the database/backend/context documentation to record the implemented
  boundary while leaving Ticket 45 open for Task 013.
- Record actual results in `changes.md`, commit and push Task 012 to `master`,
  excluding `refocus.md`.

## Reuse

- Reuse the existing `monitor.users` ownership row and `User` value object from
  Task 010.
- Reuse the direct Psycopg connection/transaction style and forward-only SQL
  migration runner.
- Reuse Python standard-library `secrets`, `hashlib`, UUID and UTC datetime
  support; add no dependency or environment variable.

## Verify

- Run unit and PostgreSQL integration tests, including repeated migrations.
- Confirm two tokens for one user create independent live sessions.
- Confirm expired and revoked tokens fail with the same domain error.
- Confirm database rows contain only token digests and no plaintext-token column.
- Confirm integration-test cleanup leaves no session, user or OTP test rows.
- Run `docker compose config --quiet` and `git diff --check`.
- Confirm `refocus.md` retains SHA-256
  `8EE807DBC69F88F225D93D608DA7A5537FF2745454109F659342521B90849257`,
  remains untracked and is not committed.

## Out of scope

- FastAPI auth routes, cookies, CORS credential changes or browser login UI.
- Sliding expiry, refresh tokens, global logout, session management UI or
  automated cleanup jobs.
- Meter profiles, ledger entries, forecasts, dashboard or reminders.
- Tariffs, Rand values, payments, hardware, OCR, MQTT or ML.
- Editing or committing `refocus.md`, or modifying sibling repositories.
