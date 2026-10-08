# Task 010: OTP storage and policy

## Result

The backend now has a tested raw-SQL foundation for open passwordless email
signup. It can issue and verify OTP challenges internally, but exposes no HTTP
authentication endpoint and sends no email yet.

Any normalized email may receive a challenge. A user row is created only after a
correct, live code is consumed; later successful logins return the same user.
Neither the email nor OTP is an API token. Ticket 45 will create opaque,
HTTP-only sessions for protected endpoints.

## Database

- Added forward-only migration `002_users_and_otp_challenges.sql`.
- Added `monitor.users` with a unique normalized email and creation timestamp.
- Added `monitor.otp_challenges` with UUID, normalized email, HMAC digest,
  creation/expiry, attempt count, and used/invalidated timestamps.
- Added constraints for normalized emails, SHA-256-shaped digests, valid expiry
  and valid attempt ranges, plus an email/creation index for request policy.
- Challenges are keyed by email because the user does not exist until successful
  verification.

## Policy and security

- Codes use `secrets.randbelow` and are formatted as six zero-padded digits.
- HMAC-SHA256 binds the code to its challenge UUID and normalized email.
- Only the digest is persisted; comparison uses `hmac.compare_digest`.
- Codes expire after 10 minutes, allow five attempts, work once and are
  invalidated when a newer code is issued.
- Requests enforce a 60-second resend cooldown and five challenges per email per
  rolling hour.
- PostgreSQL advisory transaction locks serialize issue/verify decisions for one
  normalized email.
- Failed-attempt updates commit before the generic domain verification error is
  raised, preventing unlimited retries through transaction rollback.

## Configuration

- Added only `MONITOR_OTP_HMAC_SECRET`; policy values remain reviewed code
  constants instead of separate environment variables.
- Development uses a clearly marked local-only default.
- Production settings reject that committed development secret.
- No new package or service was added. Mailpit and SMTP remain Ticket 44 / Task
  011.

## Reuse

- Reused the direct Psycopg connection and transaction patterns, versioned raw
  SQL migration runner, `MONITOR_` settings and PostgreSQL integration container.
- Used Python standard-library `secrets`, `hmac` and `hashlib`; no ORM or auth
  framework was introduced.
- The OTP module exceeds the usual 100-line implementation aim because issue and
  verification transaction invariants were kept together and tested as one
  security boundary instead of being split across tickets.

## Migration impact

- Existing databases apply one new migration and retain all existing data.
- The migration creates two empty tables and one index; it does not rewrite or
  delete existing tables.
- Production will require a unique OTP HMAC secret before startup once deployed.

## Verification

- Full backend suite: 14 tests passed.
- Tests cover normalization, six-digit formatting, challenge-bound digests,
  cooldown/hour limits, newest-code invalidation, five-attempt lockout, expiry,
  one-use behavior, database constraints and create-or-reuse user behavior.
- Re-running migrations returned no pending work and records both
  `001_baseline.sql` and `002_users_and_otp_challenges.sql` once.
- Database inspection showed challenge columns only as
  `id,email,code_digest,created_at,expires_at,attempt_count,max_attempts,used_at,invalidated_at`;
  no plaintext code column exists.
- Integration-test cleanup left zero OTP challenge rows.
- Compose configuration passed and still lists only `database`, `backend` and
  `frontend`.
- `git diff --check` passed.
- `refocus.md` retained SHA-256
  `8EE807DBC69F88F225D93D608DA7A5537FF2745454109F659342521B90849257`.
- Test containers and their network were removed; the PostgreSQL volume was
  preserved.
