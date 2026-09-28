# Task 006: Frontend authenticated shell changes

## Result

- Added pinned `keycloak-js` authentication using the existing secret-free `monitor-web` client and S256 PKCE.
- Added in-memory session initialization, silent SSO callback, access-token refresh and login/logout helpers.
- Added a small bearer-authenticated `/auth/me` client.
- Replaced the placeholder with Material UI loading, signed-out, authenticated and error states displaying validated identity data only.
- Added typed Vite environment configuration and localhost-only backend CORS configuration.
- Added frontend helper tests and backend CORS tests, then marked Ticket 6 complete.

## Reuse

- Extended the existing Material UI theme and shell.
- Reused the Task 005 Keycloak realm/client and protected `/auth/me` endpoint.
- Preserved the Compose reload workflow, public `/health` endpoint and later meter-screen roadmap boundaries.

## Checks

- `npm install --ignore-scripts` updated the lockfile with zero reported vulnerabilities.
- Local `npm test` passed 5 frontend tests and `npm run build` completed the TypeScript/Vite production build.
- `docker compose -f software/dev.docker-compose.yaml config --quiet` passed.
- `python -m compileall -q software/backend/app software/backend/tests` passed.
- `docker compose -f software/dev.docker-compose.yaml up --build --detach --wait` rebuilt affected images and reported all four services healthy.
- The backend container passed all 10 pytest tests.
- After refreshing the existing named dependency volume with `npm ci`, the frontend container passed all 5 Vitest tests.
- A delayed headless-browser check rendered the signed-out Material UI state on `http://localhost:5173`.
- The browser Sign in action opened the Monitor login page through the allowed trailing-slash redirect and `code_challenge_method=S256`.
- Live CORS preflight returned HTTP 200 for `http://localhost:5173`, and `/auth/me` without a token returned HTTP 401.
- `git diff --check` passed.
- `docker compose -f software/dev.docker-compose.yaml down` removed verification containers and the network; named volumes were retained.
