# Database

PostgreSQL uses explicit SQL through Psycopg; the project does not use an ORM.
Versioned files live in `migrations/`, and the backend records each applied
filename in `schema_migrations`. Compose runs pending migrations before the API
starts.

Keep migrations forward-only, focused and safe to run in a transaction. Never
edit an applied migration; add the next numbered `.sql` file instead.

## Planned V1 data

The modular schema tickets should introduce only the data each feature needs:

- `users`, OTP/session records and ownership identifiers;
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
