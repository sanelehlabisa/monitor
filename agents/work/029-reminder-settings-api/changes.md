# Task 029: Reminder settings API

## Result

Authenticated users and configured administrators can read and save per-meter
email reminder preferences without exposing or triggering the delivery runner.

## Change and reuse

- Added GET/PATCH `/api/meters/{meter_id}/reminders` with typed values for both
  enable flags, monthly day, low-balance lead days and IANA timezone.
- Missing preferences return disabled defaults and nullable audit times.
- Reused cookie authentication, owner/admin scope and Task 027 raw-SQL storage.
- Missing and inaccessible meters share one generic 404; invalid values return
  normal request validation errors.
- Added no test-send or runner endpoint.

## Verification

- Focused live-PostgreSQL API test: `1 passed`.
- Frontend-proxy owner defaults/save and administrator read/save: passed.
- Complete backend suite: `60 passed`.
- Synthetic proxy meter, user, OTP rows and Mailpit messages were removed.
- Compose and diff checks are recorded with the batch verification in Task 030.
