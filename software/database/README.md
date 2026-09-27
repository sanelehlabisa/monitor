# Database

Planned PostgreSQL, with SQLAlchemy/Alembic introduced in Ticket 4. Ticket 7
defines device identity/ownership; Ticket 8 defines timestamped readings.

Before schema implementation, settle units (kWh versus money), decimal
precision, capture/receipt times, confidence, optional image metadata and
duplicate ingestion. Top-ups and tariffs can change balance independently
of consumption; a falling monetary balance is not automatically energy use.

Define consent, access, retention and deletion with the data model. Do not
store private photos by default or commit service volumes/database dumps.
Development persistence belongs under an ignored local path or Docker volume.
