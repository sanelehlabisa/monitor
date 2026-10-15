# Task 047: Conditional header search

## Result

Implemented in 145 changed implementation lines relative to Task 046's working
tree. The prompt records a necessary 150-line exception to the 100-line aim:
moving the existing field counts on both sides, alongside count/query/reply
guards and the user's follow-up numbering request. Only three implementation
files changed for this task; no dependencies or backend changes. No commit/push.

- Moved existing search/clear into the list header, centred between Meters and
  My/All from 600px and on its own row on phones. Hidden on meter details.
- Hidden for 0–10 unfiltered meters in the selected view; visible above 10 or
  while a draft/applied query exists. A separate unfiltered snapshot supplies
  counts, updated by full reads/create/delete, not the filtered result length.
- Applied query stays distinct from its draft. Empty drafts, zero results and
  failed Clear reads retain a usable Clear action until full reload succeeds.
  My/All resets through the existing full-list read. Search still uses server q,
  including owner-email matching; no pagination or client keyword filtering.
- Account/list generations guard old search/clear/write-follow-up responses.
  Logout resets query/counts; old replies cannot repopulate a later account.
- Added the explicitly requested display numbers to semantic ordered meter
  lists: one-based within the current view/results, unnumbered creation row,
  unchanged UUIDs, names and stored data. Existing row actions remain separate.
- Updated focused rendering checks, frontend/demo instructions and context.
  Preserved uncommitted Tasks 045–046. Full Ticket 65 remains open; next task 048.

## Reuse

- Existing MUI field, magnifier/clear icons, header, handlers and meter endpoint.
  The relocated field is one reusable MeterSearch component in AuthPanels.
- Existing built-assets preview/isolated Edge helpers with a dedicated in-memory
  mock for counts, queries, CRUD and delayed/failing replies in .tmp/task047.
  No production fixtures, real API/DB access or new test dependency.

## Verification

- PASS: all 33 frontend checks across four files and final TypeScript/Vite
  build. Existing non-blocking chunk warning remains (536.62kB minified JS).
  Updated an old always-visible search assertion after relocating the field.
- PASS: independent review, including applied-query/failed-Clear recovery and
  late reply guards for create/rename/delete plus their follow-up reads.
- PASS: five mocked-browser groups and 25 captures across
  320/390/600/768/1024/1200px: 0/1/10/11 counts, header placement and sequential
  ordinals, native Enter/server q, one/zero matches, blank draft/Clear,
  My/All, create/delete threshold crossings, last filtered row deletion,
  search/Clear failures and retry, details exclusion/true UUID routes,
  Back/Forward, pending controls and old-query logout/new-account reset.
- PASS: final desktop/phone admin headers, one-result phone, zero-result tablet
  and new-account phone screenshots inspected; no horizontal overflow.
  All API responses and CRUD were mocked: zero real requests/writes or browser
  errors. Isolated browser and temporary server closed successfully.
- Temporary checks needed selector quoting, render-readiness and native Enter
  corrections. Icon activation was scoped to buttons because MUI Tooltip also
  labels its wrapper span; these were helper issues, not app fixes. Final run
  passed against the unchanged final production build.
- PASS: git diff --check, approved scope review and unchanged source artwork
  SHA-256 values recorded in Task 045.

## Boundaries

No schema, backend SQL/API, permissions, forecast logic/wording, real/demo data,
artwork, dependency, deployment or sibling changes. No commits/pushes.
