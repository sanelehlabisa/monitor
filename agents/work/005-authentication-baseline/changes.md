# Task 005: Authentication baseline changes

## Result

- Added a reproducible local `monitor` realm with a secret-free `monitor-web` public client using Authorization Code flow and S256 PKCE.
- Added an explicit `monitor-api` access-token audience mapper and one clearly fake local development user.
- Added typed Keycloak issuer, audience and JWKS configuration.
- Added RS256 bearer-token validation against Keycloak JWKS and a protected `GET /auth/me` identity endpoint.
- Kept `GET /health` public and deferred frontend login to Ticket 6 and device credentials to Ticket 10.
- Updated repository, backend, frontend and authentication context and marked Ticket 5 complete.

## Reuse

- Extended the existing FastAPI application factory and `MONITOR_` settings.
- Reused the current Keycloak service, PostgreSQL dependency and Compose stack.
- Preserved the existing health contract and Material UI frontend boundary.

## Checks

- The realm JSON parsed successfully and `docker compose -f software/dev.docker-compose.yaml config --quiet` passed.
- `python -m compileall -q software/backend/app software/backend/tests` passed.
- The backend image rebuilt successfully with PyJWT 2.10.1 and cryptography support.
- `docker compose -f software/dev.docker-compose.yaml up --build --detach --wait` reported all four services healthy.
- `docker compose -f software/dev.docker-compose.yaml exec -T backend python -m pytest` passed all 8 tests.
- Keycloak Admin CLI confirmed the enabled realm, public client, standard flow, disabled direct grants, S256 PKCE, localhost redirect/origin, API audience mapper and fake user.
- The public health route returned HTTP 200, `/auth/me` without a token returned HTTP 401, and the realm OpenID configuration returned HTTP 200.
- The backend resolved its internal JWKS endpoint with two active keys.
- `git diff --check` passed.
- `docker compose -f software/dev.docker-compose.yaml down` removed verification containers and the network; named volumes were retained.
