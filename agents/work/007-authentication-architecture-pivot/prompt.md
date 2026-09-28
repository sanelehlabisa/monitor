# Task 007: Authentication architecture pivot

## Aim

Remove Keycloak from the active V1 architecture and leave the repository, Docker stack, frontend, backend and project documentation in a coherent state for a later passwordless email OTP implementation.

## Clarifications

- Question: Should Task 007 remove obsolete Keycloak work across the entire active project, including documentation and files that no longer apply? Answer: Yes; update all project README and documentation content and undo active Keycloak work that no longer applies.
- Question: Should email OTP, SMTP, session persistence and their database schema be implemented in this task? Answer: No; keep Task 007 focused on the architecture pivot and make those follow-up tickets.
- Question: How should completed Keycloak tickets be handled? Answer: Preserve their historical work records and Git history, mark the active roadmap entries as superseded, and use new stable ticket IDs for replacement work.

## Change

- Remove the Keycloak service, configuration, environment variables and dependencies from the development Docker stack.
- Remove active backend JWT/JWKS authentication code, configuration, endpoint wiring, tests and packages that exist only for Keycloak.
- Remove active frontend `keycloak-js` integration, callbacks and configuration while retaining the Material UI application foundation and presenting an honest email-authentication placeholder rather than a simulated login.
- Remove obsolete active Keycloak realm and database initialization artifacts; rely on Git history for recovery and retain historical task records.
- Update all applicable project context, architecture, repository-tree, software and component documentation so it describes the post-Keycloak three-service development stack and the approved email OTP/device credential direction.
- Update the roadmap without renumbering existing tickets: mark completed Keycloak tickets as superseded and add small follow-up tickets for users/device access, OTP storage, SMTP delivery, cookie sessions, protected APIs, device credentials and the email-to-dashboard frontend flow.
- Record the removed paths, documentation impact, migration impact, reuse and verification results in this task's `changes.md`.

## Reuse

- Reuse the existing PostgreSQL, FastAPI, React/Vite and Material UI foundations.
- Reuse the current Docker health-check and service dependency patterns where they remain applicable.
- Reuse the raw SQL migration approach; do not introduce SQLAlchemy.
- Preserve the existing backend-hosted OCR direction and separate future human authentication from device authentication.

## Verify

- Search the active repository for stale Keycloak runtime/configuration references and confirm any remaining references are explicitly historical or describe the superseded architecture.
- Validate the Compose configuration contains only PostgreSQL, backend and frontend application services and has no Keycloak dependency.
- Run the backend test suite and relevant static checks.
- Install/use the declared frontend dependencies as available, then run the frontend build and tests/checks defined by the project.
- Run documentation/tree consistency checks and `git diff --check`.

## Out of scope

- Implementing OTP generation, hashing, expiry, attempt limiting or rate limiting.
- Implementing SMTP delivery or development email capture.
- Creating users, devices, device-user relationships, meter-reading or OTP/session database tables.
- Implementing secure session cookies, protected human APIs or device credential ingestion.
- Implementing ESP32-CAM firmware, capture, OCR processing or reading upload behavior.
- SMS authentication, municipal integrations, top-up flows, MQTT and anomaly machine learning.
