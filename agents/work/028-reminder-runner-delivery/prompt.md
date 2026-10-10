# Task 028: Reminder runner and delivery

## Aim

Send idempotent due monthly and predicted-low-balance emails through the existing
SMTP boundary from a one-run backend command.

## Clarifications

- Question: How is execution scheduled? Answer: Provide one finite command that
  processes due reminders; production scheduling remains Ticket 57 and no
  always-running service is added now.
- Question: When is a monthly reminder due? Answer: Once on its configured local
  calendar day each month. It always sends, adding recommended kWh when a valid
  forecast exists and otherwise asking for a fresh reading.
- Question: When is a low-balance reminder due? Answer: Only for an available
  forecast at or below the configured remaining-day threshold.
- Question: How are duplicates prevented? Answer: Monthly dedupe uses local
  `YYYY-MM`; low-balance dedupe uses the predicted local run-out date. Durable
  delivery claims prevent overlapping runs from sending the same reminder.
- Question: Who receives email? Answer: The meter owner's normalized email only;
  administrator access never changes the recipient.

## Change

- Add a forward-only reminder-delivery/claim migration with meter cascade and
  unique type/dedupe keys.
- Add due-reminder selection and policy that calls only `run_forecast_model`.
- Add plain-text monthly and low-balance messages using the existing EmailSender
  and SMTP implementation.
- Add one-run `python -m app.reminder_runner` execution with useful aggregate
  counts but no addresses, forecast details or secrets in logs.
- Make failed sends retryable without marking them delivered; safely recover
  stale claims and prevent overlapping duplicate sends.
- Add policy, repository, sender and live Mailpit tests.

## Reuse

- Reuse reminder settings, raw-SQL ledger repositories, forecast boundary,
  owner email, EmailSender/SmtpEmailSender and Mailpit development capture.

## Verify

- Run focused pure and live-PostgreSQL tests plus the complete backend suite.
- Run the command twice against controlled due records and confirm Mailpit gets
  one message per dedupe key; confirm failed delivery can retry.
- Run `docker compose config --quiet` and `git diff --check`.

## Out of scope

- Background loops, Compose services, production cron configuration, HTTP/UI,
  reminder history screens, SMS, push, tariffs and payments.
