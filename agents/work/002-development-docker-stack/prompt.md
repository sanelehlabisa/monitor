# Task 002: Development Docker stack

## Aim

Create a runnable local Docker Compose development stack for Monitor with PostgreSQL, Keycloak, a minimal FastAPI placeholder and a minimal React + MUI placeholder.

## Clarifications

- Question: Should Ticket 2 include a runnable React + MUI placeholder now? Answer: Yes.
- Question: What should the Compose file be named? Answer: `software/dev.docker-compose.yaml`.
- Question: Should repository context reflect these decisions? Answer: Yes.

## Change

- Add `software/dev.docker-compose.yaml` with PostgreSQL, Keycloak, backend and frontend services.
- Add development Docker build files, pinned dependencies and minimal backend/frontend placeholders needed to run the stack with reload.
- Use Material UI for the frontend placeholder.
- Add a safe `.env.example`, persistent development volumes, localhost port bindings and placeholder health checks.
- Document setup, shutdown and reset commands, and update repository context to use the approved Compose filename and MUI choice.
- Review-size exception: the four-service Compose definition and two runnable placeholders exceed 100 implementation lines but form one approved, inseparable foundation ticket.

## Reuse

- Reuse the existing `software/backend/` and `software/frontend/` component boundaries and the development-stack requirements in `software/README.md`.
- Keep future API, authentication and user-interface behaviour in their existing roadmap tickets.

## Verify

- Validate the Compose configuration.
- Build and start the four-service stack.
- Confirm service health and backend/frontend reload-oriented development commands.
- Run the smallest relevant backend and frontend checks introduced by this task.

## Out of scope

- Production or cloud deployment.
- Database migrations and application data models.
- Keycloak realm/client integration beyond starting the development service.
- Real API, authentication, OCR, meter-reading or dashboard behaviour.
- MQTT, payments and anomaly detection.
