# Task 003: Backend baseline

## Aim

Establish a small, tested FastAPI baseline with typed environment configuration and a process-only health endpoint.

## Clarifications

- Question: Should `/health` check PostgreSQL or Keycloak? Answer: No; keep it process-only and leave dependency integration to Tickets 4 and 5.

## Change

- Add typed application settings for the environment and log level using a `MONITOR_` environment prefix.
- Refactor the placeholder into a reusable FastAPI application factory while retaining the Compose entry point.
- Define and return a typed health response containing stable service metadata.
- Add pinned test/configuration dependencies and focused tests for settings and the health endpoint.
- Update the backend environment example and documentation, then mark Ticket 3 complete after verification.

## Reuse

- Extend the current `software/backend/app/main.py` application and `/health` route.
- Preserve the existing Dockerfile, reload command and Compose health check where practical.

## Verify

- Run the backend pytest suite.
- Validate the Compose configuration.
- Rebuild the backend image and confirm the four-service stack becomes healthy.
- Check the health response through the localhost backend port.
- Run `git diff --check`.

## Out of scope

- PostgreSQL connections, SQLAlchemy models or migrations.
- Keycloak realm/client integration or authentication.
- Meter-reading endpoints, OCR, frontend integration and production deployment.
