# Task 068: Durable Monthly Reminders

## Aim

Implement Ticket 69.7.1's finite, durable monthly delivery pass without activating automatic emails.

## Clarifications

- Schedule: 09:00 UTC on the last calendar day; no user settings.
- After downtime: discover only the latest missed cycle, but retry all saved pending emails.
- Recipients: all current meter members, including newly shared users; admin access alone does not qualify.

## Change

- Add a finite monthly helper beside the existing runner, with an explicit, timezone-aware activation cutoff and injectable clock/sender. Discover no pre-activation cycles or cycles before a meter existed. Persist the selected cycle's entire member fan-out before SMTP.
- Reuse delivery rows with target-month/recipient keys (`YYYY-MM:userID`). Keep pending/sent state and original cycle keys across retries, including older saved cycles. Retain failed jobs; recover pending claims after the existing 30-minute lease.
- Own connection/commit boundaries: commit jobs before sending and each recipient's result independently. Recheck membership and claim ownership before SMTP, using consistent meter-before-delivery locks. Prevent overlapping workers from sending the same valid claim; never commit unrelated caller work. Document the unavoidable SMTP-success/DB-crash duplicate window.
- Reuse fresh forecast calculations. Label delayed check-ins with their original notification cycle separately from the current planning date; do not invent forecasts or rekey retries.
- Preserve legacy delivery rows, CLI and low-balance behavior. Legacy keys have different meanings: do not reinterpret them. Explicitly gate later activation on legacy pending/sent reconciliation and a fixed activation cutoff in 69.7.2; this task does not claim legacy backlog recovery is complete.
- Update relevant documentation and changes.md. Allow up to 250 changed implementation lines, excluding tests/docs, because raw-SQL discovery and transactional dispatch form one reviewable correctness boundary; add no framework.

## Reuse

- Existing reminder modules/schema, membership locks, ledger readers, `run_forecast_model`, message/SMTP boundary and isolated verification patterns; no new dependency or table.

## Verify

- Isolated DB and injected sender/Mailpit only: due-time boundaries, leap/year rollover, activation cutoff, latest-only discovery, current/late members and admin-only exclusion.
- Check persisted full fan-out, independent recipient commits, failed/stale retries across older cycles, concurrency/lease ownership, removal/deletion and delayed-message dates. Preserve legacy behavior and unavailable forecasts.
- Run the backend suite, confirm unchanged OpenAPI/dependencies, check documentation/whitespace and clean only task-owned verification resources. Record actual results.

## Out of scope

- Scheduler/lifespan/CLI activation, legacy reconciliation execution, HTML/UI, forecast math, API/schema/config changes, new services/dependencies, source data/mail/service actions, deployment and commits/pushes.
