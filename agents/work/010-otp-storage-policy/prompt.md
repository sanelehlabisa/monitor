# Task 010: OTP storage and policy

## Aim

Implement the raw-SQL storage and reusable backend policy layer for open passwordless email signup, without yet exposing HTTP endpoints, sending email or creating browser sessions.

## Clarifications

- Question: Who may sign in? Answer: Any email address may request a code; V1 does not use a pre-authorised allowlist.
- Question: When is a user created? Answer: Only after a valid OTP is successfully verified, never merely because a code was requested.
- Question: What protects later backend endpoints? Answer: A later random, expiring HTTP-only session cookie. Neither an email address nor an OTP is an API bearer token.
- Question: What OTP policy applies? Answer: Six random digits, 10-minute expiry, at most five verification attempts, a 60-second resend cooldown, at most five requests per normalized email per hour, one use, and a newest-code-wins rule.
- Question: How are codes stored? Answer: Store only an HMAC-SHA256 digest bound to the normalized email and record identifier, using a server secret. Never store or log plaintext codes.
- Question: Is Mailpit included? Answer: No; Task 011 adds Mailpit and SMTP delivery with minimal development configuration.
- Question: What user-owned object follows authentication? Answer: A later ticket adds nickname-only meter/property profiles, not hardware devices.
- Question: What happens to `refocus.md`? Answer: Leave it unchanged and untracked.

## Change

- Add the next forward-only raw SQL migration for normalized unique users and OTP challenge records, with timestamps, expiry, attempt count, used/invalidated state, constraints and indexes needed for per-email policy checks.
- Keep OTP challenges keyed by normalized email so a challenge can exist before the corresponding user account.
- Add typed backend OTP policy/repository code using Python standard-library `secrets`, `hmac` and `hashlib`; do not add an authentication framework or ORM.
- Normalize email consistently before persistence and comparison.
- Issue a cryptographically random zero-padded six-digit code, enforce resend/hour limits, invalidate earlier live challenges, persist only its digest and return plaintext only to the caller for the later delivery layer.
- Verify codes with constant-time comparison, enforce expiry and attempt limits, make successful use atomic, and create or return the normalized user only after success.
- Make policy failures explicit domain results/exceptions that later HTTP handlers can translate into enumeration-safe generic responses.
- Add only the OTP HMAC secret to typed settings/environment examples. Keep policy numbers as code defaults rather than multiplying environment variables.
- Add focused unit tests for normalization, generation and digest behavior plus PostgreSQL integration tests for migration constraints, limits, invalidation, failed attempts, expiry, one-use behavior and user creation.
- Review-size exception: keep issuance and verification in one transactionally tested policy unit even if the security implementation exceeds the usual 100-line aim; splitting these invariants would make the boundary harder to review safely.
- Update affected backend/database documentation and mark Ticket 43 complete after verification.
- Record results in `changes.md`, then commit and push tracked Task 010 files while excluding `refocus.md`.

## Reuse

- Reuse the existing Psycopg connection helper, transaction behavior, migration runner, settings prefix and integration-test container.
- Reuse standard-library cryptography primitives available for keyed OTP digests; do not add unnecessary packages.
- Preserve the existing three-service Compose stack. Mailpit is intentionally added in Task 011.

## Verify

- Run backend unit and PostgreSQL integration tests in the project container.
- Re-run migrations and confirm they are idempotently recorded.
- Inspect the database to confirm plaintext OTPs are never stored.
- Confirm successful verification creates one normalized user, reuse returns the same user, and request/attempt/expiry/one-use policies hold.
- Run `docker compose config --quiet` and confirm the current service list remains database, backend and frontend.
- Run `git diff --check`.
- Confirm `refocus.md` retains SHA-256 `8EE807DBC69F88F225D93D608DA7A5537FF2745454109F659342521B90849257`, remains untracked and is not committed.

## Out of scope

- HTTP authentication endpoints, cookies, sessions or protected product routes.
- SMTP, Mailpit, email templates or delivery behavior.
- IP-based throttling; the later request endpoint must add it at the HTTP boundary.
- Meter/property profiles, balance/top-up entries, forecasting or dashboard work.
- Tariffs, Rand values, payments, hardware, OCR, MQTT or ML.
- Editing or committing `refocus.md`, or modifying sibling repositories.
