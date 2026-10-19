# Task 065: Minimal Meter Sharing

## Status

Approved by the user with "i approve 065". Implementation and isolated/mocked
verification are complete. The user subsequently authorized committing/pushing
this completed work to master on 19 October 2026; the prompt's earlier exclusion
describes its implementation-time authority, not the later Git handoff.

## Implementation

- Added optional mine=true to GET /api/meters using the existing scoped SQL.
  Omitted/false preserves existing behavior and never widens regular-user access.
- Replaced creator-email filtering with scoped server requests throughout My/All,
  search, clear, creation/rename reloads and unfiltered counts. Explicit next-view
  requests avoid stale React state; old tab results cannot replace the new scope.
- Added typed member helpers and a meter-local Sharing panel below History.
  Expansion loads members; Add shares by email, Remove/Leave confirm membership-only
  deletion. Last-member/access/validation failures remain visible; failed drafts stay.
- Successful changes enter a read-only refresh/retry state before follow-up GETs.
  Retry cannot repeat a saved POST/DELETE. Shared writes, membership reads and
  follow-up lists ignore stale account/meter/view results. Only the matching global
  list request releases its busy flag; stale replies cannot replace data/errors.
- Self-leave clears immediately and prunes My (not admin All), then returns to
  the scoped list. Its reload runs after the route reset so a failed read retains
  its GET-only Retry. Admins
  retain backend All access. Active-query sharing refreshes the unfiltered count
  too, including admin self-join through a direct meter link.
- Sharing requests disable conflicting name/ledger/Refresh controls through one
  pending callback; Back/Sign out remain available. This avoids a sharing list
  generation superseding an in-flight name save and stranding its busy state.
- Relabelled creator metadata Created by and search Name or member email.
  Theme, routes, forecast/ledger math, auth, reminders and permanent Delete stay.

## Inspection and reuse

- Read current agent instructions/context/rules, prompt template and frontend
  Ticket 69.5 requirements. Inspected App list/navigation/version state, API
  helpers/tests, meter list/details, ledger controls and backend meter scope.
- Existing admin My filtering compares creator email in two places, so a scoped
  backend query is needed; avoid per-row member requests or client-side inference.
- Reuse existing member list/share/remove endpoints and raw SQL. Missing-account
  provisioning, OTP policy, DB types and last-member safety are already implemented.
- Independent read-only planning review recommends a single on-demand local panel
  and existing request-generation patterns, with async mocked interaction checks.
  The prompt records the necessary implementation-size exception and scope limits.
- Preserve selected scope on every list reload and use the next view explicitly
  on tab changes. After membership edits, re-run active server search; successful
  writes with failed refresh must not be retried as duplicate writes.

## Checks and limits

The worktree was clean on master at preparation start (784d594). Independent
prompt/runtime reviews checked permission boundaries, retries, counts and stale
navigation. Changed current READMEs/context; preserved historical work records.

- Backend: all 92 checks passed in 26.98s, including two new integration cases for
  admin current membership/shared-in/left meters, combined name/member-email q,
  deduplication and immediate removal; regular-user false/true isolation, last-member,
  invalid flag and signed-out cases. Used a fresh isolated database and Mailpit.
- OpenAPI comparison with Task 064: only optional mine:boolean default false added;
  existing schema/operations are otherwise identical. SHA256:
  2cdb93fe2d6e4aee72a600947ca359691004fadeb214dadee9259ac5181fc8ab.
  All six installed backend dependency pins match; no requirements changed.
- Final frozen-source frontend run: all 36 checks passed in 29.50s; TypeScript/Vite
  production build passed (931 modules, Vite 10.85s). Existing >500 kB chunk warning
  only. All 12 installed frontend dependency versions match lockfile pins.
  An intermediate concurrent build saw the pending-callback prop cutover and
  failed type checking; the final frozen rebuild includes the completed wiring
  and test callback and passes. No dependency or host node_modules repair was made.
- All 12 mocked-browser groups passed: on-demand Add/Remove; validation/draft and
  last-member recovery; saved-write/read-only Retry; conflicting-control release;
  ordinary/admin My leave with failed refresh; admin All leave retaining access;
  membership My/All/q and threshold counts; self-join/full-count refresh; late
  member/list/write replies after meter/account changes; nonmember 404 recovery.
  Six captures at 1200/390/320px show no overflow or nested buttons. Root visually
  inspected the open 320px view. Browser errors, unexpected blocked requests and
  real API calls are all zero. These are mocked UI checks, not live OTP/household
  validation. Harness-only ordering/account-membership/loading assertions were
  corrected before the final replay; no application failures were hidden.
- Backend cleanup verified: exact three task containers, one fresh volume and one
  internal network removed. Three exact-owned network-none frontend build containers
  were removed after label/read-only-mount checks. The owned browser and loopback
  preview server are closed; ignored build/evidence/profile files remain.
  No broad prune, source data query or service action.
  Evidence: .tmp/task065-backend/comparison.json and summary-065-dc04fa610884.json.
  Frontend evidence: .tmp/task065/build-result.json, results.json and
  browser-cleanup.json; final build-b268a662-8a9/cleanup.json.
- Read-only Docker metadata confirms the four source containers retain Task 064's
  IDs/images/start times, are running/healthy and have restart count zero. The DB
  retains monitor-dev_postgres-data; no source restart/rebuild/SQL action occurred.
- Anonymous metadata/static reads verify the running backend serves the optional
  mine contract and Vite serves the hot-reloaded SharingPanel/pending wiring.
  No live session, OTP, customer row, SMTP or mutation was used.
- Relative links in the five current context/README files and whitespace checks
  pass. Protected schema/domain/model/research/dependency/config/brand sources
  have no diff. Implementation is 305 changed lines including the new panel,
  within the approved 400-line exception (tests/docs excluded).
- No SQL/schema/seed, role/auth, dependency, model/research, reminder, environment,
  live fixture/login/mail or sibling-repository change. Source services are left
  as found; approved bind-mounted source reload is the only runtime update.
