# Task 062: Frontend route layout

## Changes and reuse

- Split `AuthPanels.tsx` into `routes/login/LoginPage.tsx` and meter-only
  `MeterSection`/`MeterSearch` components. Split `MeterWorkspace.tsx` into
  `routes/meters/MetersPage.tsx` and `MeterDetailsPage.tsx`.
- Move Forecast/Ledger panels and the unchanged manual route helper into the
  meter route group; move Navigation to `components/`, and API/date helpers plus
  the existing theme to `lib/`. Helper tests remain colocated. No re-export shims,
  routing/state dependency, new hook layer or duplicate API client was added.
- Keep App's coordinated state, effects, handlers and request-version guards.
  Preserve list/detail keys, selected-content/ledger keys, inline name editing,
  form reset, login return and existing URLs; login is not a new `/login` route.
- Update only the frontend README's source layout/theme path, preserving Task
  060's DB-role correction and all pending work. Root/context updates are owned
  separately by the main agent. The approved move/extraction line-budget
  exception applies; no UI, wording, calculation or feature change was intended.

## Verification

- All 33 existing frontend checks pass locally with `npm.cmd test`; assertions
  were retained, with imports and list/detail fixture props updated only.
- Default PowerShell `npm` was blocked by the local execution policy. The local
  `npm.cmd run build` then exposed missing declarations in the existing MUI icon
  dependency cache. No dependency, lockfile, compiler suppression or source
  workaround was added; the local cache remains unchanged.
- Repeat all 33 checks and `npm run build` in a disposable, network-disabled
  cached frontend development image with narrowly read-only mounted current
  source/public/package/config files. All 12 direct installed dependency versions
  match package.json and package-lock.json. TypeScript and Vite pass; fresh
  `index-D9H8Q_cO.js` is 531.95 kB (166.41 kB gzip). The existing >500 kB chunk
  warning remains outside this structural task.
- Independent main-agent comparison against `09db59a` confirms App's complete
  controller state/effect/handler body and the extracted theme literal are
  unchanged. Existing assertions and route/component keys were reviewed too.
- Three focused mocked-browser groups pass with nine captures at 320/390/1200px:
  direct-ID login return/session restoration and Back/Forward; My/All threshold,
  server owner-email search/Clear and list/detail rename; both ledger save/refresh
  paths, unsaved-form remount reset, read error/retry and late-dashboard logout
  invalidation. No horizontal overflow, nested buttons, browser errors or real
  API requests occurred. Monitor identity/footer remain intact; phone and desktop
  captures were visually inspected.
- An initial browser helper incorrectly searched body text for a name displayed
  only in an input. Only the ignored helper assertion was corrected; the final
  run exits 0. Local evidence is under ignored `.tmp/task062/` (`results.json`,
  build logs/pin results and screenshots), not committed validation fixtures.
- Stale source imports and scoped whitespace checks pass. These mocked checks
  are not live authentication, database, household or deployment validation.

## Preservation and cleanup

Original frontend sources were clean tracked files before this task. Git object
availability was verified for the two superseded mixed files at commit
`09db59a7d8ced4879f48d8534cb3b1e5dc101864`:

- `software/frontend/src/AuthPanels.tsx`: blob
  `eee1d5bd5b2afb2fd81bd6121a172092468461df`.
- `software/frontend/src/MeterWorkspace.tsx`: blob
  `e4bd7444024a46b964136da25e1f33686c85a07f`.

Their implementation remains in the extracted pages/components; Git retains
their original recovery copies. Other moved sources remain under the paths in
the frontend README. No unique research/design sources, archives, backups,
refocus.md or historical work records were removed.

The main agent confirmed source backend/frontend/Mailpit stopped before edits.
No live services or DB/API were used. The isolated build container was removed
only after ID/name/label/network/read-only-mount checks. Both browser attempts
closed only their owned process trees and preview servers; final PID 13644 is
absent. No source starts/restarts, real emails, data writes, commits or pushes.
