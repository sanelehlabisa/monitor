# Database

PostgreSQL uses explicit SQL through Psycopg; the project does not use an ORM.
Versioned files live in `migrations/` and the backend records each applied
filename in `schema_migrations`. Compose runs pending migrations before the API
starts. Ticket 7 defines device identity/ownership; Ticket 8 defines timestamped
readings.

Keep migrations forward-only, focused and safe to run in a transaction. Never
edit an applied migration; add the next numbered `.sql` file instead.

Before schema implementation, settle units (kWh versus money), decimal
precision, capture/receipt times, confidence, optional image metadata and
duplicate ingestion. Top-ups and tariffs can change balance independently
of consumption; a falling monetary balance is not automatically energy use.

Define consent, access, retention and deletion with the data model. Do not
store private photos by default or commit service volumes/database dumps.
Development persistence belongs under an ignored local path or Docker volume.
