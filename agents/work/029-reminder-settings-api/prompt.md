# Task 029: Reminder settings API

## Aim

Expose authenticated per-meter reminder preferences without exposing or
triggering the delivery runner.

## Clarifications

- Question: What routes are added? Answer: GET and PATCH
  `/api/meters/{meter_id}/reminders`.
- Question: What access rules apply? Answer: Regular users manage their meters;
  configured admins retain the same unrestricted management scope.
- Question: How is timezone validated? Answer: Require a valid IANA timezone
  name and return the normalized stored value.
- Question: Can the API send a test reminder? Answer: No. Saving preferences and
  executing delivery remain separate responsibilities.

## Change

- Add typed request/response models for both enable flags, monthly day,
  low-balance lead days and timezone.
- Reuse Task 027 get/upsert functions and established generic meter 404 behavior.
- Preserve disabled defaults until a client explicitly saves settings.
- Add integration tests for defaults, save/update, invalid values/timezones,
  regular-user isolation and administrator management.

## Reuse

- Reuse cookie authentication, meter scope, validation/error conventions and
  raw-SQL reminder settings repository.

## Verify

- Run focused live-PostgreSQL API tests and the complete backend suite.
- Exercise regular-user/admin reads and updates through the frontend proxy.
- Run `docker compose config --quiet` and `git diff --check`.

## Out of scope

- Sending email, manual runner triggers, delivery history, UI, scheduler setup,
  SMS and push notifications.
