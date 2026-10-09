# Task 012: Session storage and policy

## Result

The backend now has a minimal raw-SQL session boundary for verified users.
Sessions support independent browser/device sign-ins and can be authenticated or
revoked internally; FastAPI routes and cookie transport remain Task 013.

## Database and policy

- Added forward-only migration `003_user_sessions.sql` with session UUID, user
  ownership, unique token digest, creation/expiry and optional revocation times.
- Added digest-shape, expiry and revocation chronology constraints plus indexes
  for digest and per-user access.
- Generated URL-safe tokens from 32 random bytes and stored only SHA-256 digests.
- Excluded the plaintext token from the created-session representation to reduce
  accidental disclosure in logs or debugging output.
- Used a fixed 30-day lifetime with multiple simultaneous sessions per user.
- Returned the same domain error for empty, expired, revoked and unknown tokens.
- Cascading user deletion removes that user's sessions; no background cleanup or
  global logout behavior was introduced.

## Reuse

- Reused Task 010's `monitor.users` row and typed `User` result.
- Reused the existing direct Psycopg transactions and forward-only migration
  runner without an ORM.
- Used only Python standard-library randomness, hashing, UUID and UTC datetime
  support; no dependency or environment variable was added.
- Implementation modestly exceeds the 100-line aim because the forward migration
  and complete create/authenticate/revoke security boundary were kept together.

## Verification

- Full backend suite: 26 tests passed.
- Tests cover 256-bit token generation, deterministic digests, multiple sessions
  for one user, lookup, exact expiry, revocation and generic failure behavior.
- Re-running migrations succeeded and records migrations 001 through 003 once.
- Database inspection showed only
  `id,user_id,token_digest,created_at,expires_at,revoked_at`; there is no plaintext
  token column.
- Integration-test cleanup left zero sessions, users and OTP challenges.
- `docker compose config --quiet`, Python compilation and `git diff --check`
  passed.
- Temporary containers and their network were removed after verification; the
  PostgreSQL and frontend dependency volumes were preserved.
- `refocus.md` retained SHA-256
  `8EE807DBC69F88F225D93D608DA7A5537FF2745454109F659342521B90849257`,
  remained untracked and was excluded from the commit.
