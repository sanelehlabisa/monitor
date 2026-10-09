# Task 018: Meter management and admin UI

## Aim

Complete meter-profile management so users manage their own meters and admins
can clearly identify and manage every user's meters.

## Clarifications

- Question: Are administrators read-only? Answer: No. Configured administrators
  may perform all supported operations on every existing meter.
- Question: What can normal users manage? Answer: Every supported operation on
  meters they own, with no visibility into other users' meters.
- Question: How is admin status shown? Answer: Use a small Admin indicator and
  show each accessible meter's owner email only in the administrator experience.

## Change

- Add rename and confirmed-delete actions to the selected-meter UI.
- Present owner email and a clear administrator state when `/api/me` reports an
  admin, while keeping the standard user's list uncluttered.
- Ensure mutations refresh or update list/selection state safely and surface
  duplicate, missing, and network errors.
- Add frontend tests for owner and administrator views plus rename/delete flows.
- Run a two-user end-to-end access check, update the Ticket 49 documentation,
  and record results in changes.md.

## Reuse

- Reuse the Task 016 authorization/API responses and Task 017 meter list,
  selection, feedback, and responsive MUI components.

## Verify

- Run frontend tests/build and the full backend suite.
- Verify a normal user cannot see or mutate another user's meter, while the
  configured admin can list, rename, and delete it.
- Inspect desktop/mobile states and run `git diff --check`.

## Out of scope

- Creating meters on behalf of another user, user administration, persisted
  roles, balance/top-up entries, forecasts, reminders, tariffs, payments,
  hardware, OCR, MQTT, and ML.
