# Task 011: Mailpit email delivery

## Result

The backend can now issue a Task 010 login code and deliver it through a small
SMTP boundary. Development captures messages in a pinned Mailpit service whose
web UI is loopback-only; authentication HTTP endpoints and sessions remain
Ticket 45.

## Delivery and configuration

- Added `EmailSender`, a standard-library SMTP implementation and a plain-text
  Roventics Monitor sign-in message.
- Returned only challenge UUID/expiry after delivery; plaintext remains local to
  issuance and message construction and is never logged or persisted.
- Invalidated a challenge after delivery failure while retaining its database
  row so failures cannot bypass resend/hour limits.
- Mirrored Job Talk's tracked environment convention: `SMTP_HOST`, `SMTP_PORT`,
  `SMTP_SECURE`, `SMTP_USER`, `SMTP_PASSWORD` and `EMAIL_FROM`.
- Masked the typed SMTP password. False secure mode opportunistically upgrades
  with STARTTLS; implicit TLS is available when secure mode is true; credentials
  are rejected unless the connection is encrypted.

## Development stack

- Added official `axllent/mailpit:v1.31.4` with its built-in `readyz` health
  command and made backend startup wait for it.
- Published only Mailpit's UI as `127.0.0.1:8025`; SMTP port 1025 remains on the
  internal Compose network.
- Kept API health independent from SMTP after startup. No email framework or
  other Python dependency was added.
- Implementation exceeds the usual 100-line aim because the SMTP modes,
  credential-safety rule and challenge invalidation were kept together as one
  tested security boundary.

## Reuse

- Reused Task 010's normalized email, random code, HMAC digest, policy and raw
  Psycopg transaction boundary.
- Reused Job Talk's tracked SMTP names and standard-library TLS shape without
  reading real environment values or modifying that sibling repository.
- Reused existing Compose health/dependency and loopback binding patterns.

## Verification

- Full backend suite: 22 tests passed.
- Tests cover message content, Mailpit-style plain SMTP, STARTTLS, implicit TLS,
  encrypted authentication, secret masking, failed-send invalidation and typed
  environment loading.
- A live integration test delivered a generated six-digit OTP through SMTP,
  read it through Mailpit for only the requested recipient and matched it to the
  HMAC-only PostgreSQL digest.
- PostgreSQL integration-test cleanup left no Task 011 challenge/user records.
- PostgreSQL, Mailpit, backend and frontend reported healthy; API health returned
  OK and Mailpit `readyz` returned HTTP 200.
- Mailpit UI resolved to `127.0.0.1:8025`; Compose reported no published port for
  SMTP 1025.
- `docker compose config --quiet`, Python compilation and `git diff --check`
  passed.
- Temporary containers and their network were removed after verification; the
  PostgreSQL and frontend dependency volumes were preserved.
- `refocus.md` retained SHA-256
  `8EE807DBC69F88F225D93D608DA7A5537FF2745454109F659342521B90849257`,
  remained untracked and was excluded from the commit.
