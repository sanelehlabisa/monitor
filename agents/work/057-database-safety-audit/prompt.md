# Task 057: Existing database safety audit

## Aim

Complete Ticket 69.1's data audit and verified recovery gate before changing
database initialization or administrator authority.

## Clarifications

- Preserve all current users, meters, history and other existing database state.
  No reset or replacement of the current database is approved.
- This starts the batch with 69.1 only. Tasks 058/69.2 and 059/69.3 require the
  audit findings and their own approved prompts before implementation.

## Change

- Resolve the exact development database, container, volume and PostgreSQL
  version. Inspect schema, migration state, counts, constraints and relationships
  using read-only source transactions; do not expose row contents or credentials.
- Make a consistent backup with PostgreSQL tools. Plan a new dedicated directory
  under %LOCALAPPDATA%/Monitor/backups/task057/, resolving and checking the actual
  path before writing. Keep it outside OneDrive/Git, never overwrite an existing
  backup, retain its SHA-256 and treat it as sensitive, not encrypted by default.
- Restore only into uniquely labelled disposable PostgreSQL resources, without
  the source volume, published ports or app/email workers. Match the backup and
  inventory snapshot; verify restored schema, records and usable sequences.
- Retain the verified backup and recovery instructions. After checks, remove only
  positively identified task-owned disposable resources, never the source or
  recovery backup. Report exact retained/removed paths and resource identities.
- Review the minimal nine-table target and propose a data-preserving additive
  transition for 058/059. Keep owner-query compatibility until sharing cutover,
  account for later owner-to-membership backfill, and review existing-user role
  assignment without executing it. Restoring the old schema is not an upgrade.
- Update the database README, relevant context and changes.md with non-identifying
  results and readiness/remaining decisions. Use task-local verification helpers
  only as needed; no new runtime dependency or permanent backup service.

## Reuse

- Existing Compose, PostgreSQL tools, raw SQL schema/migrations, Psycopg and the
  preservation/compatibility requirements recorded under Ticket 69.

## Verify

- Compare matching-snapshot table counts and private record fingerprints, FKs,
  ledger amounts/times, migration state and identity sequences after restoration.
- Verify the source was not modified; keep sensitive artefacts out of chat/Git.
- Check recovery instructions, allowed file scope, links and whitespace; record
  actual checks and limitations, not assumed recovery success.

## Out of scope

- Source writes, resets, migrations, seeding, role changes, source/container or
  Docker Desktop restarts, application/SQL/config/.env changes, emails, sharing
  or forecast implementation, siblings, commits and pushes. If source/Docker
  access is unavailable, report it without restarting or resetting services.
