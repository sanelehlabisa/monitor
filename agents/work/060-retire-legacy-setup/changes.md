# Task 060: Retire legacy setup and stale context

## Result

Complete, including isolated checks and resource cleanup. No commit/push.

## Changes and reuse

- Removed the eight inactive numbered SQL migrations, applied upgrade-058.sql
  and retired app/migrations.py. Removed only the obsolete runner rejection
  test/imports, retaining database/bootstrap checks. Removed empty init/ and
  migrations/ after exact-path and empty-content checks.
- Active database/ now contains schema.sql, seed.sql and README.md only. Reused
  the existing fresh setup without SQL/seed modifications. No stored tables or
  source records were changed; both database history tables remain preserved.
- Replaced historical active context with current contracts/structure/next gates;
  shortened AGENTS.md's inactive CAD detail while preserving workflow, data,
  research/design-source protection and non-invasive hardware rules.
- Corrected active role/setup guidance and recorded stable roadmap tickets 71-73.
  Replaced superseded software setup/UI iteration narrative with current features.
  Existing historical work records, refocus.md, research/archives and all pending
  Task 059 edits were preserved. Backend/frontend reorganization is separate.

## Recovery before deletion

- Independently verified all ten deleted files were recoverable from Git commit
  09db59a7d8ced4879f48d8534cb3b1e5dc101864, with normalized content unchanged.
- Archived 34 pending-source/retired-file entries before editing under ignored
  .tmp/task060/pre-cleanup-source.zip. Every ZIP entry matched current source
  SHA-256 byte-for-byte before deletion. Archive SHA-256:
  b6741fc6719fa70a3f226c9cb9f0a6e4f94dccfbd2e20d0cc72b93f7b7f4e2c4.
  Recover an individual path from this archive into a separate staging directory
  and compare it first; do not overwrite current work or extract a whole baseline
  over the working tree. The archive is local/ignored, not a portable Git artifact.
- Exact retained SQL copy:
  %LOCALAPPDATA%/Monitor/backups/task059/20261018T171408Z-4fbf46c4c3c5/reviewed-upgrade-058.sql.
  SHA-256 c5ad664ee3e3febe924a9d096c802bbbbb1dd4363aff40c1f95d83943e9a3fe2
  matched both this copy and the deleted working file. Initial restricted read
  was denied; an approved escalated hash-only check then verified the copy.
  Backups/recovery evidence were not edited or removed.

## Checks and limits

- Read-only preflight retained source DB ID
  06438f44071a29fb405b6afc8569e1dcaa575b3c23163b0fcd3f75c7f658dd4e,
  volume monitor-dev_postgres-data, running with unchanged start/restart metadata;
  backend/frontend/Mailpit were exited. No source-service action was performed.
- Dependency search found no active Compose/runner consumers; only the retired
  test imported it. Retained ignored old verification helpers are historical,
  not advertised as current upgrade commands.
- git diff --check passed (existing CRLF/global-ignore access warnings remain).
- All 67 remaining backend checks passed in 30.54s against a fresh isolated
  nine-table DB and captured Mailpit, with current code mounted read-only and
  cached dependency versions matching requirements. No pytest warnings reported.
  One obsolete runner check was removed; no other assertions were dropped.
- Canonical OpenAPI baseline SHA-256:
  32c5aba6aa94d8a9473b9a0b286c5b0fc6c1f913bdbe7b511fd4e579784e04a7.
  Safe summary: .tmp/task060/summary-060-9ea728993a59.json. Detailed synthetic
  verification evidence is retained under %LOCALAPPDATA%/Monitor/backups/task060/
  20261018T180503Z-060-9ea728993a59/. Source actions/queries were both false.
- Active Markdown file links passed. At 2026-10-18T18:07:17Z, all three owned
  containers, one synthetic DB volume and one internal network were removed
  after recorded ID/label/mount/network checks. Task labels were absent afterward;
  source resources/images and private evidence remained untouched.
  No live-browser/source-HTTP result or fresh image build claimed.
- Final read-only source metadata check after the batch retained the same four
  container IDs, source database volume, start times and zero restart counts.
  PostgreSQL was healthy/running; frontend/backend/Mailpit remained exited.

Deletion-only implementation size exceeds 100 lines as approved; no feature added.
