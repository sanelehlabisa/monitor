# Task 002: Development Docker stack changes

## Result

- Added `software/dev.docker-compose.yaml` with PostgreSQL, Keycloak, backend and frontend services, loopback-only ports, persistent volumes and health checks.
- Added pinned development images and dependencies, an npm lockfile, Docker build files and a sanitised `.env.example`.
- Added minimal reloadable FastAPI and React + Material UI placeholders.
- Added the Keycloak database bootstrap and documented start, stop and reset commands.
- Updated project context and component READMEs with the approved Compose filename and Material UI choice.

## Reuse

- Reused the existing `software/backend/`, `software/frontend/`, `software/database/` and `software/keycloak/` component boundaries.
- Kept API, migrations, realm integration and application behaviour in their existing later roadmap tickets.

## Checks

- `docker compose -f software/dev.docker-compose.yaml config --quiet` passed.
- `python -m compileall -q software/backend/app` passed.
- `npm.cmd ci --ignore-scripts` installed the lockfile with zero reported vulnerabilities.
- `npm.cmd run build` passed with TypeScript 7.0.2 and Vite 8.3.1.
- `docker compose -f software/dev.docker-compose.yaml up --build --detach --wait` built the images and reported all four services healthy.
- Local endpoint checks returned backend `status=ok`, frontend HTTP 200 with the expected title, and Keycloak HTTP 200.
- `git diff --check` passed.
- `docker compose -f software/dev.docker-compose.yaml down` removed test containers and the network; named development volumes were retained.
