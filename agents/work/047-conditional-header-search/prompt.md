# Task 047: Conditional header search

## Aim

Keep small meter lists uncluttered while retaining search for larger lists.

## Clarifications

- Show search only above 10 meters in the selected view: agreed.
- Centre it between Meters and My/All on tablets/desktop; use its own row on
  phones. Keep it visible while filtering, including zero results.
- Follow-up user request: add simple one-based row numbers to the visible meter
  list, restarting after filtering/view changes; actual meter IDs stay unchanged.

## Change

- Move the existing search/clear field into the meter-list header; remove its
  separate content row. Do not show it on a meter-details page.
- Base visibility on the unfiltered selected-view count, not filtered results.
  Keep counts correct after creation/deletion and My/All or account changes.
- Preserve server-side name/owner-email search, Enter, clear, pending/error
  handling, keyboard accessibility and the open layout.
- Number visible meter rows without changing names, IDs or API data.
- Review-size exception: relocating the existing field counts as both removed
  and added lines. Allow up to 150 changed implementation lines for that move,
  unfiltered counts, applied-query/reply guards and requested row numbering;
  keep the change within the existing three frontend components.
- Update frontend README, context, focused checks and changes.md. Preserve
  uncommitted Tasks 045–046; aim for at most 100 implementation lines changed.

## Reuse

- Existing MUI search field/icons, list endpoint and handlers; no dependencies
  or duplicate client-side keyword filtering.

## Verify

- Frontend tests, TypeScript/Vite build and git diff --check.
- Counts 0/1/10/11; active searches with zero/one match, clear, My/All and
  creation/deletion crossing the threshold. Phone/tablet/desktop header layout.

## Out of scope

- Pagination, backend/schema/data changes, new features beyond search visibility,
  forecasting, permissions, full Ticket 65 review, siblings, commits and pushes.
