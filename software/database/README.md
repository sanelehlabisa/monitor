# Database

PostgreSQL uses explicit SQL through Psycopg; the project does not use an ORM.
Versioned files live in `migrations/`, and the backend records each applied
filename in `schema_migrations`. Compose runs pending migrations before the API
starts.

Keep migrations forward-only, focused and safe to run in a transaction. Never
edit an applied migration; add the next numbered `.sql` file instead.

## Implemented authentication data

Migration `002_users_and_otp_challenges.sql` adds:

- `monitor.users`: unique normalized email and creation time; and
- `monitor.otp_challenges`: challenge UUID, normalized email, HMAC digest,
  creation/expiry, attempt count and used/invalidated timestamps.

Challenges intentionally reference email rather than a user ID because open
signup creates the user only after successful verification. Constraints reject
non-normalized emails, non-SHA256-shaped digests, invalid expiry and invalid
attempt counts. The email/creation index supports cooldown and hourly limits.

Plaintext OTPs are never persisted. Forecasts and sessions are not stored by this
migration.

Migration `003_user_sessions.sql` adds `monitor.user_sessions`. Each row belongs
to a verified user and stores a unique SHA-256 digest, creation/expiry times and
an optional revocation time. The plaintext 256-bit random token exists only when
the session is created for the future cookie layer. A user may have multiple
independent sessions, each with a fixed 30-day lifetime.

## Planned product data

The modular schema tickets should introduce only the data each feature needs:

- nickname-only `meters` or meter/property profiles owned by a user;
- actual `balance_entries` with non-negative kWh and occurrence timestamps; and
- `top_up_entries` with positive kWh and occurrence timestamps.

Names are planning guidance until their migration tickets approve exact tables,
columns, constraints and indexes. Store event times consistently (UTC in storage,
local presentation at the UI boundary) and retain creation/update audit times for
corrections.

V1 does not require device tables, image metadata, confidence scores, tariffs,
Rand amounts or municipal meter identifiers. Sharing one meter between multiple
users is deferred; every query must enforce the owning user.

Forecasts should be derived from ledger history rather than stored as if they
were actual readings. If cached later, preserve inputs/versioning so estimates
remain distinguishable and reproducible.

Define retention, correction and deletion behavior with the data tickets. Do not
commit service volumes, database dumps, customer information or private bills.
