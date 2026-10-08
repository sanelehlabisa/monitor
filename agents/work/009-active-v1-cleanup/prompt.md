# Task 009: Active V1 cleanup

## Aim

Complete roadmap Ticket 48 by aligning the current application shell with the approved software-only manual-kWh V1 and confirming obsolete hardware/OCR/device assumptions are absent from active runtime code and configuration.

## Clarifications

- Question: Does the runtime contain device, OCR or camera implementation that must be removed? Answer: No; the audit found only generic FastAPI, PostgreSQL, Docker and Material UI foundations.
- Question: What implementation change is needed? Answer: Replace the frontend placeholder's generic meter-reading wording with concise manual balance/top-up kWh planning language and update its test.
- Question: Should authentication, schemas or APIs be implemented now? Answer: No; retain the disabled email-auth placeholder and leave feature work to its modular roadmap tickets.
- Question: What happens to deferred research and brand sources? Answer: Preserve hardware/OCR folders unchanged and defer logo selection/copying to the approved dashboard UI ticket.
- Question: What happens to `refocus.md`? Answer: Leave it unchanged and untracked.

## Change

- Update `software/frontend/src/App.tsx` so the current Material UI card describes the software-only V1: quick manual balance and top-up entries in kWh, transparent estimates and inactive email authentication.
- Keep all controls visibly disabled so the shell does not imply that authentication or data entry already works.
- Keep the layout compact and mobile-first, reusing the existing Material UI structure and the approved interaction principles observed in the sibling Switch UI without copying code or assets.
- Update the frontend static-render test to assert the new product boundary and disabled state.
- Audit active non-document source, dependencies, environment examples and Compose configuration for obsolete Keycloak, device-ingestion, camera or OCR runtime assumptions; remove only confirmed stale active artifacts if any are found.
- Mark Ticket 48 complete in the root roadmap and record actual cleanup/audit results in `changes.md`.
- Commit and push the tracked Task 009 work after verification, while explicitly excluding `refocus.md`.

## Reuse

- Reuse the existing React/Vite, Material UI theme, responsive card layout and static-render test pattern.
- Reuse the existing FastAPI, PostgreSQL, raw-SQL and three-service Compose foundations without changing them when the audit confirms they are generic.
- Treat `../switch/hardware/web/` as read-only design inspiration only; do not modify sibling repositories or copy their implementation.

## Verify

- Run the frontend test suite and production build.
- Confirm the rendered shell states manual kWh balance/top-up planning and does not claim working authentication, data entry or forecasts.
- Search active non-document runtime/configuration files for stale Keycloak, device-ingestion, camera and OCR assumptions.
- Validate the Compose service list remains PostgreSQL, backend and frontend if configuration changes become necessary.
- Run `git diff --check`.
- Confirm `refocus.md` retains SHA-256 `8EE807DBC69F88F225D93D608DA7A5537FF2745454109F659342521B90849257`, remains untracked and is not committed.

## Out of scope

- Email OTP, SMTP, cookie sessions or authenticated routes.
- Users, meter profiles, balance entries, top-up entries or database migrations.
- Forecasting functions, dashboard/history APIs, working forms or reminders.
- Tariffs, Rand values, payments, hardware, firmware, OCR, MQTT or ML.
- Copying a logo or other assets into Monitor.
- Editing deferred research files, `refocus.md`, or either sibling repository.
