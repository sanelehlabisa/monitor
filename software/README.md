# Monitor software

Planned path: image/reading -> OCR where selected -> REST API -> PostgreSQL ->
web UI. Nothing is runnable yet; this ticket creates documentation only.

## Components

- [Backend](backend/README.md): FastAPI API and configuration.
- [Database](database/README.md): PostgreSQL and migration plan.
- [Authentication](keycloak/README.md): Keycloak users and separate device access.
- [Frontend](frontend/README.md): React balance/history/status.
- [OCR](ocr/README.md): simple recognition of one meter from PC photo fixtures.

## Development stack (Ticket 2)

Create `docker-compose.dev.yml`, `.env.example` and Docker build files within
this software tree. Actual `.env` stays local and ignored. Provide Postgres,
Keycloak, backend and frontend services, backend/frontend reload, persistent
development data and documented setup/reset steps. Keep local services bound
to localhost where practical, and do not publish credentials or an unsecured
stack to the internet.

Ticket 2 may introduce only minimal service placeholders needed to start the
stack; API/config tests (3), migrations (4), realm integration (5) and frontend
behaviour (6) remain separate. Select and pin compatible dependency/image
versions during implementation, not speculative versions in this scaffold.

Production deployment, MQTT, payment integration and OCR implementation are
out of scope. Use consented data with explicit retention/access rules.
