# Task 069: Automatic Monthly Reminders

## Aim

Finish Ticket 69.7.2 and the agreed monthly-only Ticket 69 scope with automatic delivery and safe local activation.

## Clarifications

- Monthly planning only; shared/automatic low-balance alerts are deferred. Preserve the existing opt-in low-balance code without scheduling it.
- Keep 09:00 UTC on month-end, current members, latest-missed-cycle discovery and all saved new-format pending retries.
- No backup work. Proposed activation starts from the next future month-end, using a fixed first-activation cutoff saved across restarts.

## Change

- Add one optional, timezone-aware UTC activation setting, persisted in ignored `.env` and wired through Compose/examples. Empty disables automation; reject invalid/naive values. Never reset the cutoff on startup or silently enable production.
- Add a lifespan-owned asyncio loop: immediate startup recovery, sequential checks every 60 seconds, blocking work off the event loop, safe error logging and cooperative stop/worker draining. Bound reminder-only DB waits and retain SMTP timeouts; allow Docker sufficient shutdown grace. Do not cancel a thread and assume sending stopped, or start overlapping passes.
- Reuse Task 068's finite pass, claims, membership checks and fresh forecasts. Check monthly delivery-key compatibility before each automatic pass; unresolved legacy/malformed rows block sending without deleting, remapping or falsely completing them. Existing sent records stay intact.
- After isolated checks, inspect only aggregate current delivery status and non-secret mail-target/runtime metadata. If compatibility is clear and SMTP is the existing internal Mailpit capture, save the first-activation cutoff and recreate only the backend once. Leave database/frontend/Mailpit running. Otherwise keep activation off and report the required decision. Do not repeat recreation after a failed health/activation check; report the actual backend/scheduler state. No forced reminders, source test records or external SMTP sends.
- Add a small schedule note in collapsed Sharing, without settings or a layout change. Update current docs/results and defer shared low-balance automation explicitly. Mark Ticket 69 complete only after checks and activation gates pass.
- Allow up to 250 changed implementation/config lines, excluding tests/docs: lifecycle, bounded worker shutdown and explicit activation are one review boundary. Add no dependency, service or schema.

## Reuse

- `monthly_reminders`, existing SQL/SMTP/forecast helpers, FastAPI app factory/settings, Compose, Sharing UI and isolated Task 068 verification patterns.

## Verify

- Isolated lifecycle tests: disabled/invalid settings, startup/catch-up, sequential retry after failure, overlap protection, legacy blocking, responsive requests and shutdown during work. Preserve all existing backend behavior/OpenAPI and frontend flows.
- Run backend checks, relevant frontend checks/build and isolated Mailpit delivery; inspect Compose without exposing secrets. Confirm the single-backend activation, fixed cutoff and other service identities; clean only task-owned resources and record actual results.

## Out of scope

- Low-balance automation, HTML email, model changes, schema upgrades/resets, backups, source ledger/auth/member writes, external mail, VPS deployment, unrelated UI changes and commits/pushes. Unresolved legacy reconciliation needs a separate approved plan.
