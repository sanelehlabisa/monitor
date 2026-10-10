# Task 028: Reminder runner and delivery

## Result

Monitor can process opted-in reminder settings once, deliver due messages through
the established SMTP boundary and avoid normal duplicate sends.

## Change and reuse

- Added durable reminder delivery claims with monthly/run-out dedupe keys,
  stale-claim recovery and retry release after SMTP failure.
- Added monthly and predicted-low-balance policy using stored local timezone and
  the single `run_forecast_model` boundary.
- Added plain-text messages to the meter owner through existing
  `EmailSender`/`SmtpEmailSender` implementations.
- Added finite `python -m app.reminder_runner` execution with aggregate-only
  output suitable for later external scheduling.
- Added no background loop, Compose service or production scheduler.

## Verification

- Focused reminder policy/claim/retry tests: 4 passed.
- Complete backend suite: 59 passed.
- Live one-run command against a synthetic opted-in meter delivered two Mailpit
  messages on its first run and zero on its second; the second run reported two
  duplicate skips. The messages and synthetic database user were removed.
- Failed SMTP delivery releases claims for retry; active and sent claims remain
  unavailable, while stale pending claims can recover after 30 minutes.
- `docker compose config --quiet` and `git diff --check` passed.
