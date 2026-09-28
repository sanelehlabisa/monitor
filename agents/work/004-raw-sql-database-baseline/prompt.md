# Task 004: Raw SQL database baseline

## Aim

Establish a PostgreSQL baseline using explicit SQL and Psycopg, with repeatable versioned migrations and tested backend connectivity.

## Clarifications

- Question: Should the database baseline use SQLAlchemy and Alembic? Answer: No; use real SQL and no ORM.
- Question: Should it include a lightweight migration runner and connectivity test? Answer: Yes.
- Question: Where may OCR run initially? Answer: Prefer backend-hosted OCR when it helps build and iterate on the AI-assisted proof of concept quickly; record the direction now but do not implement OCR in this task.

## Change

- Replace the planned SQLAlchemy/Alembic direction in project documentation with Psycopg and versioned PostgreSQL SQL files.
- Add typed database connection configuration and a small reusable Psycopg connection helper.
- Add a migration runner that records applied SQL files and safely skips them on later runs.
- Add an initial baseline migration without device or reading tables.
- Run migrations before the development backend starts and add focused configuration, connectivity and migration tests.
- Record backend-hosted OCR as the preferred initial integration direction for rapid iteration, subject to later accuracy and performance measurements.

## Reuse

- Extend the existing backend `Settings`, Docker image and Compose database dependency.
- Reuse the current PostgreSQL service and `software/database/` component boundary.
- Keep the existing process-only `/health` contract unchanged.

## Verify

- Run the backend pytest suite.
- Validate the Compose configuration and rebuild the backend image.
- Start the four-service stack and confirm every service becomes healthy.
- Apply migrations twice and verify the baseline version is recorded only once.
- Run a direct `SELECT 1` connectivity check through the backend helper.
- Run `git diff --check`.

## Out of scope

- SQLAlchemy, Alembic or another ORM.
- Device, ownership or meter-reading tables and queries.
- Authentication integration or changing `/health` to probe dependencies.
- OCR code, models, datasets, image storage or inference endpoints.
- Production database credentials, backups, deployment or destructive reset tooling.
