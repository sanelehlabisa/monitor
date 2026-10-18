# Task 057: Existing database safety audit

## Result

Completed 69.1's technical audit/recovery gate, preserving the existing database.
The additive target proposal remains subject to review; 058/69.2 and 059/69.3
need their own approved prompts. No upgrade, reset or role change was executed.

Initial attempts found Docker unavailable, then all Monitor containers stopped.
The user subsequently approved starting **only** the existing database. That
explicit exception to the prompt's no-start/restart scope was used once; Docker
Desktop and the other services were not restarted or started.

## Verified source and retained recovery

- Source: monitor-dev-database-1, ID
  eb141cc3d5c25822608f8e4c8738bfc13b6ab0cb51fcf473879291646896af93.
- Existing volume: monitor-dev_postgres-data at /var/lib/postgresql/data.
- Running PostgreSQL: 17.11; configured image postgres:17.11-alpine3.24;
  source and restore used exact image ID
  sha256:b0f9560a2de083e2cc7382e75f808c7381a32852a7ec49117deedb300e552b24.
- Private retained directory:
  C:\Users\hlabi\AppData\Local\Monitor\backups\task057\20261018T161738Z-452d70772a48.
  The resolved path is outside Git/OneDrive; a new exclusive directory was used
  and its ACL restricted to the Windows user and SYSTEM. It is not encrypted.
- monitor.dump: 25,316 bytes; SHA-256
  3cc92a4cb840559c50f98409a52bef6e9c47114a20a897726f389c72c17fd959.
- Retained alongside it: backup-manifest.json, reference.json, restored.json,
  source-after.json, planned-target.json, restore-target.json,
  verified-summary.json, cleanup-summary.json, private diagnostics and RECOVERY.md.
  These contain sensitive backup/security metadata or private fingerprints;
  none is committed or reproduced in chat. The guide was copied byte-identically
  before cleanup. The archive hash was checked again before removal.

## Actual checks

- Reviewed required guidance, component README, all eight migrations, runner,
  Compose and the approved preservation plan. Independent read-only reviews
  checked source compatibility, backup methodology and cleanup boundaries.
- Held a REPEATABLE READ READ ONLY source transaction and exported its snapshot.
  The complete-database pg_dump custom archive (--create, --snapshot) and private
  canonical all-table inventory used that same snapshot. Binary subprocess
  output went directly to an exclusively created archive, not a text pipeline.
- Restored with pg_restore --exit-on-error --create to a distinct control
  database on the same image, preserving database/object ownership and ACLs.
  The disposable target had its own labelled volume, network none, no published
  ports and no application/email workers. Readiness checked the final server.
- Compared all records through private canonical SHA-256 fingerprints, including
  exact IDs, auth digests/security state, numeric ledger values and all times.
  Compared columns, constraints/FKs, indexes, both migration histories, schemas,
  ownership/ACLs/default ACLs, extensions, settings, policies, views, functions,
  triggers, sequence definitions and sequence state. All matched.
- Tested nextval only on the clone: first next value matched the captured state
  and exceeded the largest existing identity. No source nextval/setval occurred.
- A fresh read-only source inventory matched the pre-backup inventory. Container
  ID/start time/restart count also matched after the audit. The approved server
  startup changes physical files normally; this is logical-state preservation,
  not byte-for-byte physical-volume immutability.

Observed counts (no row contents):

| Table | Rows |
| --- | ---: |
| monitor.users | 2 |
| monitor.meters | 4 |
| monitor.balance_entries | 7 |
| monitor.top_up_entries | 4 |
| monitor.otp_challenges | 16 |
| monitor.user_sessions | 16 |
| monitor.reminder_settings | 0 |
| monitor.reminder_deliveries | 0 |
| monitor.schema_migrations | 8 |
| public.schema_migrations | 1 |

Ten physical tables: eight domain tables plus **two** bookkeeping tables.
Verified catalog totals: 38 constraints, 21 indexes, one sequence. A monitor-only
dump would omit public.schema_migrations; preserve both histories in later work.

## Cleanup and limits

After independently checking exact IDs, task/token labels, the single clone
mount, source exclusion, isolation and retained archive/hash/guide, removed only:

- Container monitor-task057-452d70772a48, ID
  e06db3751a42496eb0a3467ad0d38f74bc22a1c874e5d8f49948805135b72304.
- Volume monitor-task057-452d70772a48-data.

Post-cleanup checks found no resources with that task/token, confirmed the source
ID/volume and healthy database, and confirmed backend/frontend/Mailpit still
exited. The removed clone is recoverable from the retained verified archive;
the original volume and backup were never deleted. No broad prune or stack-down
operation was used. Cleanup proof was retained at 2026-10-18T16:21:42Z.

This is a logical single-database recovery check, not a cluster/global backup:
role definitions/passwords and tablespaces are not included. Original ownership/
ACLs matched under the original principal in isolation; other role dependencies
need review. Sequence counters are non-MVCC; matching captured counters here
must not imply snapshot-exact counters during concurrent writes. Other Monitor
workers were off. Restoring the old schema proves recovery, not compatibility
or correctness of a future upgrade. RECOVERY.md is a future operator recipe,
not a second completed restore or permission to overwrite the source.

## Proposal, reuse and handoff

Keep the nine-domain-table target (existing eight plus user_meters), without
dropping either historical bookkeeping table. Preserve security/ledger state,
constraints and derived per-meter rates. Proposed future conversion is additive:
constrained users.type default user and unique user/meter memberships. Retain
meters.user_id, owner joins/name indexes/API fields until sharing cutover;
repeat owner-to-membership backfill then for interim owner-only creations.
Resolve creator-delete cascades/last-member protection with shared access.

Coordinate fresh schema.sql/seed.sql initialization with retiring migration
startup; fresh init is not an existing-volume upgrade. An explicitly approved,
separately rehearsed additive transition and one-time existing-admin assignment
are needed before DB-only authority. No runtime email override or environment
bootstrap should substitute for that mapping. Exact future DDL and role updates
belong to 058/059 approval, not this audit.

Updated only database README, agent context and 057 work records. Reused native
PostgreSQL/Docker tools, existing SQL/Compose, Python standard library in the
existing local research environment, and temporary ignored verification helpers.
No runtime dependency or permanent backup service was added. No application,
SQL/config/.env, research, sibling, real email, source write, commit or push.
No application suite was run because application behaviour did not change.

Final checks passed: git diff --check, explicit whitespace checks on all four
changed/new Markdown files, and all local Markdown link targets. Git scope is
only agents/context.md, software/database/README.md and 057 prompt/changes;
temporary helpers/guide are ignored. No SQL/runtime/config/root-roadmap/refocus
diff exists. Git's existing LF/CRLF and inaccessible global-ignore warnings did
not prevent these checks. Independent read-only review passed the recovery
recipe/cleanup guards. A final Docker read confirmed the healthy source,
three stopped services and absence of the exact task-labelled clone/volume.
