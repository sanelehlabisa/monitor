# Task 030: Reminder settings UI

## Aim

Let users opt into and configure simple per-meter email reminders from the
selected-meter Material UI workspace.

## Clarifications

- Question: What is the default UI state? Answer: Both reminder types are off;
  monthly day defaults to 1 and low-balance lead time to 3 days.
- Question: Which timezone is saved? Answer: Use the browser's resolved IANA
  timezone when no preference exists and display it beside the controls.
- Question: What choices are shown? Answer: Monthly email with day 1-28 and an
  optional predicted-low-balance email with lead days.
- Question: What does the UI promise? Answer: Email reminders only; it never
  claims to buy electricity or guarantee forecast accuracy.

## Change

- Add typed reminder GET/PATCH client functions.
- Add a compact settings section with independent MUI switches, constrained
  numeric inputs, timezone text and one explicit save action.
- Load settings with the selected meter and keep user/admin behavior identical.
- Show loading, saved, validation, missing-resource and request-error feedback.
- Explain that monthly email can request a fresh reading when no estimate is
  available and low-balance email requires a valid forecast.
- Add component/API tests for defaults, enabled states, timezone and feedback.

## Reuse

- Reuse selected-meter state, session-aware API helper, Material UI feedback and
  the established owner/admin backend policy.

## Verify

- Run frontend tests and production build plus the complete backend suite.
- Validate save/reload for regular-user and administrator access through the
  frontend proxy.
- Run `docker compose config --quiet` and `git diff --check`.

## Out of scope

- Browser-side scheduling, test-send buttons, delivery history, SMS, push,
  automated purchases, tariffs, Rand amounts, hardware, OCR and ML.
