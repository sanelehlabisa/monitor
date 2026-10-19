# Task 065: Minimal Meter Sharing

## Aim

Complete Ticket 69.5 with simple sharing controls and membership-based My filtering.

## Clarifications

- Confirmed: one collapsed Sharing section below History; forecasts stay first.
- Reuse existing permissions: any member/admin manages sharing, leaving removes
  membership only, last-member removal is rejected and admins retain global access.

## Change

- Add optional mine=true to GET /api/meters, reusing existing membership SQL and
  keyword search. Preserve default behavior; regular users never gain global scope.
- Use server scope for every My/All list/search/reload and its unfiltered count;
  remove creator-email filtering. Keep existing search visibility and race guards.
- Add typed member API calls and one meter-local Sharing panel: load on expansion,
  email Add, member list and confirmed Remove/Leave actions. Label creator metadata
  Created by; search wording uses member email. No invitations or new accounts UI.
  Remove/Leave deletes only membership; permanent meter Delete is unchanged.
- Show validation, last-member and access errors; retain failed drafts. Separate
  successful writes from failed reloads so Retry never repeats a saved mutation.
  Refresh scoped lists/search after changes; self-leave clears the workspace and
  returns to the list, including admins without changing their global authority.
- Ignore stale responses/errors after account, meter or view changes. Keep the
  theme, routes, ledger, forecast calculations and navigation unchanged.
- Update README/context and changes.md. Allow up to 400 implementation lines
  (expected 250-350; tests/docs excluded) for this cohesive API/UI safety flow;
  reuse existing patterns, not a new abstraction or framework.

## Reuse

- Existing member endpoints, raw-SQL scope, api.ts, meter routes, MUI controls,
  confirmation patterns and version guards. Keep the running development stack;
  normal source hot reload only, no service restart/rebuild.

## Verify

- Check combined mine/keyword scope, admin membership and regular-user isolation.
- Run frontend checks/build plus mocked desktop/phone interaction checks for
  sharing, removal/leave, last-member errors, scoped search, failed reload recovery
  and stale replies after meter/account changes, including self-leave followed by
  failed list refresh. Include member, non-member and global-admin cases.
- Use only mocked/isolated data for writes; preserve live DB/mail/services.
  Clean exact-owned test resources and check links, whitespace and API compatibility.

## Out of scope

- Schema upgrades, live fixtures/login/mail, auth/role changes, forecast/reminder
  work, new routes/dependencies, redesign, service actions, backup/research deletion,
  sibling repositories, commits or pushes.
