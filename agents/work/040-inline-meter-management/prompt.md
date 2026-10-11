# Task 040: Inline meter management

## Aim

Make meter management available inline while keeping the planning UI simple (Ticket 63).

## Clarifications

- Account icon: increase the current 28px size by 1.5 to 42px.
- Selected meter: use Name/Owner key-value rows, an editable name input and
  a pencil-only save action; remove the bottom Meter settings section.
- Action placement: the user confirmed pencil/trash icons on each meter-list
  row. Keep the existing delete confirmation.

## Change

- Enlarge the account icon without changing the right-aligned account menu.
- Show Name and read-only Owner rows above the selected meter's planning card.
  Save name changes using the pencil icon or Enter.
- Put pencil/trash actions on every accessible meter-list row. The pencil opens
  an inline name editor; pencil/Enter saves and Escape cancels. Deletion confirms
  the named meter first. Actions must not accidentally open the meter.
- Remove bottom Meter settings. Preserve loading/error feedback and disable
  conflicting actions during saves. Give icon-only controls accessible labels.
- Reuse shared rename/delete handlers for list and selected-meter actions;
  preserve ownership, admin access, search and meter-ID navigation.
- Update README/context and record checks in changes.md. Aim for 100 changed
  implementation lines; allow up to 200 for the shared-handler/list-row refactor.
  Preserve all existing uncommitted Tasks 037–039.

## Reuse

- Existing MeterWorkspace, Navigation, MUI icons, authenticated meter APIs,
  rename/delete confirmation handlers and local browser-check helpers.

## Verify

- Check desktop/320px/390px layouts, 42px icon, key-value alignment and no overflow.
- Verify inline rename/save/cancel, delete cancellation/confirmation, error states
  and navigation using disposable meters; check regular-user and admin actions.
- Keep retained demo histories unchanged. Run relevant frontend checks, the
  asset build and diff check; record actual results.

## Out of scope

- Backend/schema, forecast math, permissions, demo histories, dependencies,
  branding, deployment and sibling repositories. No commit or push.
