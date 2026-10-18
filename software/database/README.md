# Database

PostgreSQL uses explicit SQL through Psycopg; the project does not use an ORM.

## Current implementation

Versioned files live in `migrations/`, and the backend records each applied
filename in `schema_migrations`. Compose runs pending migrations before the API
starts. There are eight Monitor-domain tables plus this bookkeeping table.

Keep migrations forward-only, focused and safe to run in a transaction. Never
edit an applied migration; add the next numbered `.sql` file instead.

### Implemented tables

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
an optional revocation time. The plaintext 256-bit random token is delivered
through the existing HTTP-only cookie layer, not persisted. A user may have
multiple independent sessions, each with a fixed 30-day lifetime.

Migration `004_meter_profiles.sql` adds nickname-only `monitor.meters`. Each
meter has an application-generated UUID, one owning user, a trimmed 1-80
character name and creation/update timestamps. Names are case-insensitively
unique per owner. The raw-SQL repository provides owner-scoped CRUD plus an
explicit unrestricted scope for the administrator API.

Migration `005_balance_entries.sql` adds factual remaining-kWh observations.
Each UUID entry belongs to one meter, stores non-negative `NUMERIC(12,3)` kWh,
an occurrence time and creation/update timestamps. A meter cannot have two
actual balances at the same occurrence time. Deleting its meter cascades to its
balance history.

Migration `006_top_up_entries.sql` adds manually purchased energy events. Each
UUID entry belongs to one meter, stores positive `NUMERIC(12,3)` kWh plus
occurrence/audit timestamps, and is deleted with its meter. Multiple purchases
may share an occurrence time and are ordered deterministically by UUID.

Migration `007_reminder_settings.sql` adds one optional preference row per
meter. Monthly and predicted-low-balance emails are independently disabled by
default. Saved settings constrain monthly days to 1-28, positive warning lead
days to at most 30, and a trimmed IANA timezone name. Rows cascade with their
meter; email delivery history is introduced separately.

Migration `008_reminder_deliveries.sql` adds durable monthly/low-balance claims
with unique per-meter type/dedupe keys. Pending claims may be recovered by the
runner after a timeout; successful sends record their completion time. Rows
cascade with the meter and do not duplicate the owner's email address.

## Planned database/access refocus: Ticket 69

Task 056 plans the following work only. It changes no SQL, initialization,
permissions or data. Each implementation needs its own approved prompt; the
current migration and owner-scoping policies above remain active until replaced.
The [root roadmap](../../README.md) owns execution order; backend details for
69.3 roles and 69.4 membership are in the [backend README](../backend/README.md).

### 69.1: Existing-data audit, backup/restore and target-schema review

Dependencies: none within Ticket 69. Inspect the exact development database and
volume before proposing an upgrade or reset. Identify records to preserve without
committing their contents. Produce a backup/recovery procedure and verify a backup
by restoring it to a separate disposable database, checking row counts, ledger
values/times and relationships. Never overwrite the source to test restoration.

The minimal target is nine domain tables, retaining existing names:

- `users`: normalized email, audit time and planned `type` (`user`/`admin`).
- `otp_challenges`: email-keyed signup challenges with digest, expiry, attempts,
  consumed/invalidated state and existing cooldown/rate-limit support.
- `user_sessions`: user FK, unique token digest, expiry and revocation state.
- `meters`: UUID, name and audit times, with membership replacing sole ownership.
- `user_meters`: user/meter FKs and a unique composite membership key.
- `balance_entries`: meter FK, non-negative kWh, occurrence/audit times and the
  existing unique per-meter occurrence constraint.
- `top_up_entries`: meter FK, positive kWh and occurrence/audit times; multiple
  purchases at the same time remain valid.
- `reminder_settings`: retain planning/low-balance configuration separately.
- `reminder_deliveries`: retain durable delivery claims/deduplication separately;
  69.7 defines per-recipient keys and member-removal handling.

Keep open email signup and secure cookie sessions: users are created only after
verification, and plaintext OTPs/session tokens never enter the database. Preserve
`occurred_at` separately from insertion/update times so historical manual entries
remain meaningful. Use timezone-aware UTC instants for storage and local display
at the client boundary. Consumption rates and forecasts remain derived from each
meter's ledger, not a second authoritative stored value or a new model.

Acceptance: approve exact keys, constraints, essential indexes and recovery
evidence; explicitly choose preservation/upgrade versus a disposable reset before
69.2. Membership must prevent last-member removal, including concurrent removals
and account deletion; 69.4 defines transactional enforcement. Settle creator
display, sharing onboarding and whole-meter deletion with 69.4/69.5 prompts.
Saved reminder timezone/send time is resolved with 69.7, not inferred from UTC.
Do not introduce triggers, stored procedures or extra tables without a need.

### 69.2: Fresh SQL files and persistent Docker initialization

Depends on 69.1's approved target and data decision. Add `schema.sql` and
`seed.sql`, mounted in order for PostgreSQL fresh-volume initialization. Replace
the active numbered-migration startup dependency only in this implementation;
update dependent checks/documentation and record recovery before retiring sources.
Do not rewrite applied migrations now or execute a reset during normal startup.

Keep each intermediate release compatible with the running API/UI. Retain owner
columns/constraints required by current queries and backfill initial memberships
as an additive bridge until 69.4/69.5 cut over; alternatively stage activation of
the final schema with those integrations. Do not activate a membership-only schema
while the application still requires sole ownership.

Keep the named PostgreSQL volume and backend/frontend hot reload. Initialization
scripts run only on a new empty database volume: container restart/recreation
does not reapply schema or seeds, upgrade an existing volume or erase records.
Document a separately approved existing-data upgrade/reset path and explicit
backup/restore commands. Verify restoration in a disposable target first.

Seeds contain only small fictional meter/ledger examples and the explicitly
approved fresh-setup admin account `hlabisasanele730@gmail.com`. With 69.3, the DB
is the sole user/admin authority: new verified signups default to `user`; later
role changes are direct DB updates. This admin seed runs only at fresh setup,
never as an email override, environment fallback or restart-time promotion that
undoes a changed role. Retire admin environment configuration in 69.3, not now.
The seeded role may exist before 69.3, but environment configuration remains the
implemented runtime authority until that separate backend integration is complete.

Acceptance: fresh schema/seed loading, valid FKs/kWh/UTC data and known admin
role; compatible OTP/session and meter/ledger reads; persistence after container
restart/recreation; no seed replay or role re-promotion; working hot reload and
documented backup/restore. Verify 69.3/69.4 authorization behavior when those
dependent integrations land, not merely because their tables exist.

Tariffs, Rand amounts, hardware/OCR data and forecast-model adoption remain out
of scope. Never commit service volumes, database dumps or private customer data.
