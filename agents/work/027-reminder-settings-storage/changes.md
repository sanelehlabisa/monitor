# Task 027: Reminder settings storage

## Result

Per-meter monthly and low-balance email preferences now have constrained raw-SQL
storage while remaining safely disabled until explicitly saved.

## Change and reuse

- Added migration `007_reminder_settings.sql` with meter cascade, enable flags,
  monthly day 1-28, positive lead days, IANA timezone and audit timestamps.
- Added typed get/upsert repository functions using established meter scope.
- Missing rows return disabled defaults without silently writing or enabling
  email; callers may provide the browser timezone for that initial view.
- Reused Psycopg, meter access and Decimal validation patterns; no ORM or new
  environment setting was introduced.

## Verification

- Focused live-PostgreSQL repository tests: 2 passed.
- Complete backend suite: 55 passed.
- Covered disabled defaults, save/update values, owner/admin scope, runtime and
  database validation, IANA timezone validation and meter cascade deletion.
- `git diff --check` passed with only line-ending notices.
