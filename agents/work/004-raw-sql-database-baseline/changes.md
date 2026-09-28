# Task 004: Raw SQL database baseline changes

## Result

- Added direct PostgreSQL connectivity through pinned Psycopg with typed `MONITOR_DATABASE_URL` configuration.
- Added a lightweight migration runner that applies ordered SQL files transactionally and records each filename in `schema_migrations`.
- Added the initial `001_baseline.sql` migration, which creates the `monitor` schema without introducing domain tables.
- Updated Compose to mount and apply migrations before Uvicorn starts.
- Added integration coverage for connectivity and migration idempotency.
- Replaced the planned SQLAlchemy/Alembic direction with explicit SQL in project documentation.
- Recorded backend-hosted OCR as the preferred initial integration for rapid iteration; no OCR implementation was added.

## Reuse

- Extended the existing backend settings, image and Compose database dependency.
- Reused the PostgreSQL service and `software/database/` component boundary.
- Preserved the process-only `/health` contract and deferred device/reading tables to Tickets 7 and 8.

## Checks

- `docker compose -f software/dev.docker-compose.yaml config --quiet` passed.
- `python -m compileall -q software/backend/app software/backend/tests` passed.
- The backend image rebuilt successfully with Psycopg 3.3.2 on Python 3.14.4.
- `docker compose -f software/dev.docker-compose.yaml up --build --detach --wait` applied one baseline migration and reported all four services healthy.
- `docker compose -f software/dev.docker-compose.yaml exec -T backend python -m pytest` passed all 5 tests.
- Two explicit reruns of `python -m app.migrations` each applied zero migrations.
- The backend helper returned `Connected=True` for `SELECT 1`, and `schema_migrations` contained only `001_baseline.sql`.
- `git diff --check` passed.
- `docker compose -f software/dev.docker-compose.yaml down` removed verification containers and the network; named volumes were retained.
