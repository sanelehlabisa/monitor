# Task 011: Mailpit email delivery

## Aim

Implement a minimal SMTP abstraction and OTP email delivery service backed by an isolated Mailpit development service, without exposing authentication HTTP endpoints or creating sessions.

## Clarifications

- Question: Which development mail service should be used? Answer: Pin official Mailpit `v1.31.4`; its web UI uses port 8025 and SMTP uses port 1025.
- Question: How is Mailpit exposed? Answer: Bind only the web UI to loopback port 8025. Keep SMTP available only on the internal Compose network.
- Question: How should development mail configuration match Job Talk? Answer: Reuse its tracked `.env.example` convention: `SMTP_HOST`, `SMTP_PORT`, `SMTP_SECURE`, `SMTP_USER`, `SMTP_PASSWORD` and `EMAIL_FROM`, including the note that false uses STARTTLS when available while true uses implicit TLS. Do not read or copy a real `.env` file.
- Question: Is a console fallback required? Answer: No; development email must be observable through Mailpit.
- Question: What happens after OTP verification? Answer: Ticket 45 later creates a random HTTP-only session cookie. This task only delivers the code created by Task 010.
- Question: What happens to `refocus.md`? Answer: Leave it unchanged and untracked.

## Change

- Add `axllent/mailpit:v1.31.4` to development Compose with its built-in readiness check, loopback-only web UI on port 8025 and no host SMTP port.
- Make the backend wait for healthy Mailpit in development while keeping API process health independent of SMTP availability after startup.
- Add typed settings for the six Job Talk-style SMTP variables, with Mailpit development defaults supplied by Compose.
- Keep passwords masked in typed settings/log representations and never log an OTP or SMTP credentials.
- Add a small email-sender protocol and standard-library SMTP implementation; do not add a mail framework.
- The implementation may exceed the usual 100-line aim so plain SMTP,
  STARTTLS, implicit TLS, credential safety and failure invalidation remain one
  reviewable delivery boundary instead of being split across partially safe
  tickets.
- Add a plain-text OTP message with the six-digit code, 10-minute expiry, a warning not to share it and instructions to ignore an unrequested message.
- Add an orchestration function that issues the Task 010 challenge and sends its email. If SMTP delivery fails, invalidate that challenge and raise a delivery-domain error without exposing the code.
- Preserve the request count on delivery failure so an attacker cannot bypass rate limits by forcing SMTP failures.
- Add unit tests for typed configuration, message content, SMTP modes/credentials and failure invalidation.
- Add a container integration test proving a generated OTP reaches Mailpit for only the requested recipient and the database still stores only its digest.
- Update environment examples and affected README/context/roadmap entries, including the Mailpit UI address and Ticket 44 completion.
- Record results in `changes.md`, then commit and push tracked Task 011 files to `master` while excluding `refocus.md`.

## Reuse

- Reuse Task 010's issuance, HMAC storage, expiry and invalidation boundary.
- Reuse Job Talk's tracked SMTP environment naming and standard-library `email`, `smtplib` and `ssl` approach rather than adding a dependency; do not modify the sibling repository.
- Reuse the established Compose health/dependency and loopback-binding patterns.
- Use Mailpit's official built-in `readyz` container health command and API for integration verification.

## Verify

- Run backend unit and PostgreSQL integration tests.
- Build/start the development stack and confirm healthy `database`, `mailpit`, `backend` and `frontend` services.
- Trigger one OTP delivery and verify recipient, subject, safe body and six-digit code through the Mailpit API.
- Confirm the matching database row contains only `code_digest`, not plaintext.
- Confirm SMTP port 1025 is not published to the host and Mailpit UI is reachable only on `127.0.0.1:8025`.
- Run `docker compose config --quiet` and `git diff --check`.
- Confirm `refocus.md` retains SHA-256 `8EE807DBC69F88F225D93D608DA7A5537FF2745454109F659342521B90849257`, remains untracked and is not committed.

## Out of scope

- OTP request/verify HTTP endpoints, enumeration-safe HTTP responses, cookie sessions or protected routes.
- HTML email design, attachments, marketing messages, SMS or push notifications.
- Production SMTP provider selection, DNS records or deployment secrets.
- Meter profiles, balance/top-up entries, forecasts, dashboard or reminders.
- Tariffs, Rand values, payments, hardware, OCR, MQTT or ML.
- Editing or committing `refocus.md`, or modifying sibling repositories.
