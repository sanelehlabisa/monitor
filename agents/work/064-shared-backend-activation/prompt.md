# Task 064: Activate Shared-Meter Backend

## Aim

Complete Ticket 69.4's safe existing-database transition and start the development app.

## Clarifications

- Preserve all users, meters, history, roles, sequences and both migration histories.
- Start existing frontend/backend/Mailpit only after successful verification;
  PostgreSQL stays running. No live test records, OTP emails or reminder runs.

## Change

- Confirm source DB/volume/schema, stopped apps and existing container commands/
  mounts serving committed Task 063 code. Halt on drift; no implicit recreation.
- Make a fresh hashed, private full backup; verify exact isolated restore and
  rehearse frozen, hashed bytes of Task 063's reviewed upgrade.sql on that copy.
  Recheck source preservation before execution; halt if it changed.
- Apply identical reviewed bytes once with ON_ERROR_STOP and existing
  timeouts: backfill only memberless meters and change two user FKs to RESTRICT.
  Never re-add a departed creator on an otherwise shared meter.
- Verify only intended changes; retain the backup. On failure keep apps off
  and report; no automatic restore, reset, seed replay or role changes.
- Start only the three approved existing app services, without restarting or
  recreating PostgreSQL. Check health, served UI and anonymous access denial;
  use isolated copies for authenticated/security checks.
  If startup checks fail, stop only task-started apps; keep PostgreSQL running
  and preserve the committed database/evidence for review.
- Update README/context and changes.md; close 69.4 only after all gates pass.
  Keep sharing UI under 69.5 and other roadmap IDs unchanged.

## Reuse

- Task 063 SQL, recovery/restore and isolated verification helpers, raw SQL,
  existing Compose services and the unchanged forecast/authentication contracts.

## Verify

- Compare original rows, roles, sequences, constraints and both histories before/
  after; prove only approved memberships/FKs changed. Check current-code access
  and forecasts on the copy, service identity/health and local HTTP responses.
- Clean only exact-owned disposable resources; retain private recovery/evidence,
  check documentation links and whitespace, and record actual results/limits.

## Out of scope

- Source fixtures/login sessions, real mail, reminder CLI, sharing UI, model or
  dependency changes, new services, backup deletion, siblings and Git handoff.
