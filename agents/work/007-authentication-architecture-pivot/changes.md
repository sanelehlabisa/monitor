# Task 007: Authentication architecture pivot

## Result

Keycloak has been removed from the active V1 project. The development stack now
contains PostgreSQL, FastAPI and the React/Material UI frontend. Human login is
intentionally unavailable until the approved email OTP and secure cookie-session
tickets implement it; device identity remains a separate UUID/credential boundary.

## Before and after

- Before: four Compose services, a realm import, a separate Keycloak database,
  backend JWT/JWKS validation, a bearer-protected `/auth/me` route and a
  `keycloak-js` browser session.
- After: three Compose services, a process-only `/health` API, no active auth
  endpoints, and a Material UI screen that clearly labels email authentication
  as planned and keeps its controls disabled.
- Tasks 005-006 remain unchanged as historical records. The root roadmap marks
  their implementations as superseded rather than rewriting that history.

## Changed files

- Updated `software/dev.docker-compose.yaml` and development environment examples
  to remove the Keycloak service, database bootstrap mount and auth variables.
- Simplified `software/backend/app/main.py`, `settings.py`, requirements and tests
  to remove JWT/JWKS behavior while preserving health and CORS foundations.
- Simplified `software/frontend/src/App.tsx` to the honest email-auth placeholder,
  added a static-render test, and removed `keycloak-js` from both package files.
- Updated `README.md`, `agents/context.md`, `hardware/firmware/README.md` and every
  affected software component README with the three-service stack, raw SQL policy,
  backend-hosted OCR direction, separate human/device authentication boundaries,
  local-AP owner-email setup direction and follow-up tickets.
- Added this task's approved prompt and result record.

## Removed active paths

- `software/keycloak/`
- `software/database/init/01-create-keycloak-database.sql`
- `software/backend/app/auth.py`
- `software/backend/tests/test_auth.py`
- `software/frontend/src/auth.ts` and its test
- `software/frontend/src/api.ts` and its test
- `software/frontend/src/config.ts` and `vite-env.d.ts`
- `software/frontend/public/silent-check-sso.html`
- `software/frontend/.env.example`

The removed source is recoverable from Git history, including commit `5fb8fb4`.
No unique design source or user data was deleted.

## Active software tree

```text
software/
|-- backend/       # FastAPI, Psycopg and health/CORS baseline
|-- database/      # PostgreSQL and versioned raw SQL migrations
|-- frontend/      # React and Material UI placeholder
|-- ocr/           # backend-hosted OCR experiments planned
|-- .env.example
|-- README.md
`-- dev.docker-compose.yaml
```

## Roadmap

- Tickets 5-6 are retained and marked superseded.
- Ticket 42 records this completed removal without renumbering prior tickets.
- Tickets 43-46 split OTP policy/storage, email delivery, cookie-session APIs and
  the Material UI email/OTP flow into reviewable follow-up work.
- Ticket 7 now owns raw SQL users/devices/many-to-many access; Ticket 10 retains
  independent device credentials; dependent reading/UI tickets were corrected.

## Reuse

- Retained PostgreSQL, the direct Psycopg migration runner, FastAPI application
  factory, restricted CORS origin, React/Vite and Material UI.
- Retained Docker health checks and backend/frontend development reload patterns.
- Retained backend-hosted OCR as the preferred fast PoC direction; no ORM or
  OCR implementation was introduced.

## Migration impact

- No Monitor schema migration was added, edited or applied by this task.
- Fresh databases no longer create a separate `keycloak` database.
- An existing `postgres-data` volume may still contain the unused Keycloak
  database. It is harmless and was not destructively removed; developers may
  explicitly reset local volumes using the documented `down --volumes` command.
- An old Keycloak container can appear as a Compose orphan after updating; the
  software README documents a one-time `down --remove-orphans` cleanup.
- Existing frontend dependency volumes can retain unused package files until
  refreshed with the documented `npm ci` Compose command; the lockfile no longer
  declares `keycloak-js`.

## Verification

- `docker compose -f dev.docker-compose.yaml config --services` returned only
  `database`, `backend` and `frontend`; `config --quiet` passed.
- Backend container suite: 7 tests passed.
- Frontend suite: 1 test passed.
- Frontend TypeScript/Vite production build passed (899 modules transformed).
- Frontend dependency refresh removed the obsolete local `keycloak-js` package;
  `npm ls keycloak-js --depth=0` returned an empty tree.
- A clean Compose build and startup completed; `/health` returned
  `ok, monitor-api, development` and the frontend returned HTTP 200 with the
  expected title.
- Smoke-test containers and network were removed with `down`; the database volume
  was preserved.
- Repository-local Markdown links resolved, the active reference audit found no
  stale runtime/configuration integration, and `git diff --check` passed.
