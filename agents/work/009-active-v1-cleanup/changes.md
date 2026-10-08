# Task 009: Active V1 cleanup

## Result

The current Material UI shell now reflects the software-only manual-kWh product
direction. It clearly states that balance entry, top-up entry, forecasts and
passwordless email access are not implemented yet.

The active runtime/configuration audit found no legacy device-ingestion, camera,
OCR, MQTT or Keycloak implementation to remove. The backend, database and Compose
foundations were already generic, so they were left unchanged.

## Changes

- Replaced the frontend's generic meter-monitoring copy with manual balance and
  top-up kWh planning language.
- Kept the email field and action disabled to avoid presenting unfinished
  authentication or product behavior as working.
- Explicitly states that V1 does not require hardware or OCR.
- Updated the static-render test for the product boundary and disabled state.
- Marked roadmap Ticket 48 complete in the root README.

## Audit

- No Keycloak/JWT/JWKS configuration or dependency remains.
- No device credential or `/api/device` ingestion path remains.
- No camera, ESP32, MQTT or OCR runtime integration remains.
- Compose still contains only PostgreSQL, backend and frontend.
- Deferred hardware/OCR sources and sibling repositories were not changed.
- No logo or other brand asset was copied; that remains part of a later approved
  dashboard UI task.

## Reuse

- Reused the existing React/Vite application, Material UI theme, compact card
  layout and static server-render test.
- Retained the FastAPI, PostgreSQL, raw-SQL and Docker Compose foundations without
  unnecessary edits.

## Verification

- Frontend tests: 1 passed.
- TypeScript and Vite production build passed; 899 modules transformed.
- Compose configuration passed and listed `database`, `backend` and `frontend`.
- Active non-document runtime/configuration search found no stale Keycloak,
  device-ingestion, camera, ESP32, MQTT or OCR integration.
- `git diff --check` passed.
- `refocus.md` SHA-256 remained
  `8EE807DBC69F88F225D93D608DA7A5537FF2745454109F659342521B90849257`.
- Backend tests were not rerun because backend code and configuration did not
  change.
