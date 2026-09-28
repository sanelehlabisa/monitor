# Task 006: Frontend authenticated shell

## Aim

Connect the React and Material UI shell to Keycloak login and the protected backend identity endpoint.

## Clarifications

- Question: What should the frontend baseline include? Answer: Add Keycloak login/logout, call `/auth/me` with the access token, display the authenticated username/email and allow localhost frontend access through narrowly scoped backend CORS.
- Question: What remains deferred? Answer: Keep meter balances, readings, device status and other domain screens in their later roadmap tickets.

## Change

- Add a pinned Keycloak browser dependency configured for the existing `monitor` realm and public `monitor-web` PKCE client.
- Add small authentication and API helpers for login, logout, token refresh and `/auth/me` requests.
- Replace the placeholder with Material UI loading, signed-out, authenticated and error states.
- Display only the validated username/email returned by the backend and provide login/logout actions.
- Add typed frontend environment configuration with sanitised development examples.
- Add typed backend CORS configuration restricted to the development frontend origin.
- Add focused tests for the frontend API/authentication behavior and backend CORS while preserving existing tests.
- Update frontend/backend documentation and mark Ticket 6 complete after verification.

## Reuse

- Extend the existing Material UI theme and shell rather than replacing the frontend stack.
- Reuse the Task 005 Keycloak realm/client and backend `/auth/me` endpoint.
- Preserve the current Docker Compose reload workflow and public `/health` endpoint.

## Verify

- Install from the npm lockfile, run frontend tests and build the production bundle.
- Run the backend pytest suite.
- Validate Compose and rebuild affected images.
- Start the four-service stack and confirm every service becomes healthy.
- Confirm the frontend loads, the Keycloak authorization endpoint is reachable and unauthenticated `/auth/me` remains protected.
- Run `git diff --check`.

## Out of scope

- Meter balance, reading history, trends, warnings or device-status UI.
- Device credentials, ownership or meter-reading authorization.
- Roles, administration screens, registration or password-reset flows.
- Token persistence outside Keycloak's browser session handling.
- Production domains, deployment configuration or real user accounts.
