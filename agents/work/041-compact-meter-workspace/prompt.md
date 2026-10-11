# Task 041: Compact meter workspace

## Aim

Simplify meter controls and give list/detail pages one consistent compact style (Ticket 64).

## Clarifications

- Task 041 proposal approved; the user added black section headers with rounded
  top corners: Meters for the list, `Meter <ID>` for details.
- Admin-only My/All tabs belong at the list header's far right; active is white
  with dark text. Keep detail-page styling consistent, without list filters.
- Pencil enables editing, then becomes Save. Creation goes in the first list
  row with Add; preserve name casing and use meter URLs.
- Compact text/buttons; magnifying-glass and clear-cross controls inside search.

## Change

- Apply the agreed header/tabs. Reuse edit/save behaviour on both pages:
  read-only initially, pencil focuses editing, Save/Enter persists, Escape
  cancels. Success closes editing; errors retain the draft.
- First list row: name input plus Add icon, including empty/search states.
  Keep ownership and confirmed deletion unchanged.
- Search/clear icons sit together inside the input, with accessible labels and
  tooltips. Enter searches; matching remains backend-driven.
- Remove forced uppercase, not stored casing. Proposed rem-based scale: 14px
  body/buttons, 18px headings, 20px forecast values. Compact padding; avatar stays 42px.
- List URL `/meters`; details `/meters/<uuid>`. Preserve `/` entry links,
  login return, reload, Back/Forward and unavailable-link recovery.
- Update README/context and changes.md. Aim for 100 implementation lines;
  allow 250 for this combined header/control/route refactor. Preserve Tasks 037–040.

## Reuse

- Existing MUI theme/components, route helper, CRUD/search handlers, authorised
  APIs and local browser-check helpers; no new dependencies.

## Verify

- Desktop/320px/390px: headers/tabs, casing, compact controls and no overflow.
- Disposable fixtures: creation, edit/save/cancel/retry, owner/admin filters,
  search/clear, URLs/login/navigation and deletion. Preserve demo histories.
- Frontend checks, asset build and diff check; record actual results.

## Out of scope

- Backend/schema, forecast math, permissions, dependencies, branding, deployment,
  sibling repositories and refocus.md. No commit or push.
