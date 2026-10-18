# Task 060: Retire legacy setup and stale context

## Aim

Keep only active database setup and concise current project guidance.

## Clarifications

- The user chose database/schema.sql, seed.sql and README.md only; preserve the
  database, both history tables, backups, research, work records and refocus.md.
- This cleanup precedes backend/frontend structure tasks 061/062. Preserve all
  pending Task 059 changes; no commit or source-service start is requested.

## Change

- Verify recoverable Git/private-backup copies and hashes before deleting the
  eight old migration SQL files, applied upgrade-058.sql and app/migrations.py.
  Remove empty init/ and migrations/ only after checking their exact contents.
- Remove only the retired-runner rejection test/imports, retaining other checks.
- Shorten AGENTS.md and agents/context.md to current rules, product/forecast/auth
  contracts, structure and handoff. Remove obsolete narrative/inactive CAD detail;
  retain approval workflow, data protection and non-invasive hardware safety.
- Fix stale active README guidance, including frontend admin-by-email claims;
  document the exact retained upgrade copy and SHA-256 for recovery instead of
  pointing to deleted active paths.
  Log roadmap cleanup tickets 71-73 without renumbering existing tickets.
- Record removals, recovery locations, reuse and checks in changes.md. Line-budget
  exception covers deletion of archived legacy SQL/runner code, not new features.

## Reuse

- Current schema/seed, Git history, Task 059 recovery set and existing checks.

## Verify

- Check dependencies, exact deletion scope/recovery hashes, Markdown links and
  whitespace; run the remaining backend suite on an isolated fresh DB/Mailpit.
  Keep source services/database untouched and retain temporary cleanup evidence.

## Out of scope

- Feature/model/UI changes, live DB writes/resets, service starts/restarts,
  backup/research/work-record deletion, siblings, dependencies, commits/pushes.
