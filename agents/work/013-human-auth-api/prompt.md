# Task 013: Human authentication API

## Aim

Finish Ticket 45 with a minimal FastAPI email-OTP flow that creates a secure
cookie session and protects `/api/me`.

## Clarifications

- Question: How should OTP request outcomes be exposed? Answer: For a
  syntactically valid email, always return the same HTTP 202 body when delivery
  succeeds, request policy rejects it or expected SMTP delivery fails.
- Question: How should verification failures appear? Answer: Return one generic
  HTTP 401 response for incorrect, expired, used, locked or unavailable codes.
- Question: What cookie policy should be used? Answer: Name it
  `monitor_session`; set `HttpOnly`, `SameSite=Lax`, path `/`, a 30-day maximum
  age and `Secure` outside local development.
- Question: Are multiple devices allowed? Answer: Yes; each successful
  verification creates an independent Task 012 session.
- Question: What does logout revoke? Answer: Revoke only the presented session,
  clear its cookie and return 204 even if the cookie is missing or invalid.
- Question: How is email input validated? Answer: Normalize case/whitespace and
  apply a small practical shape/length check without adding a validation package.
- Question: What happens to `refocus.md`? Answer: Leave it unchanged and
  untracked.

## Change

- Add an authentication router with `POST /api/auth/request-otp`,
  `POST /api/auth/verify-otp`, `POST /api/auth/logout` and `GET /api/me`.
- Reuse Task 011 delivery for requests and intentionally collapse only expected
  OTP policy/delivery failures into the same accepted response; unexpected
  database/programming failures must remain visible as server failures.
- Verify six-digit codes through Task 010, create a Task 012 session and return
  the normalized user's ID/email without returning either credential.
- Set the approved cookie attributes and never place email, OTP or session token
  in JSON, URLs or browser storage.
- Authenticate `/api/me` from the opaque cookie and return one generic 401 for a
  missing, expired, revoked or unknown session.
- Enable credentialed CORS only for the configured frontend origin and only the
  currently required GET/POST methods and content-type header.
- Add focused API tests plus one live PostgreSQL/Mailpit flow covering request,
  captured code, verification, cookie-authenticated `/api/me`, logout and denial
  after logout.
- Update context, roadmap and backend/software documentation; complete Ticket 45.
- Record actual results in `changes.md`, commit and push Task 013 to `master`,
  excluding `refocus.md`.
- The implementation may exceed the 100-line aim because the four-route vertical
  slice, cookie boundary and error translation must be reviewed and tested
  together; keep it in one small router with no framework or abstraction layer.

## Reuse

- Reuse Task 010 verification/user creation, Task 011 email delivery and Task
  012 create/authenticate/revoke session functions.
- Reuse the application factory, typed settings, direct Psycopg connector and
  existing single-origin CORS middleware.
- Use FastAPI/Pydantic features already installed; add no dependency, session
  secret or environment variable.

## Verify

- Run the full backend suite and repeat all migrations.
- Prove a new email can request a code, receive it through Mailpit, verify it,
  access `/api/me`, log out and then receive 401.
- Confirm request responses are identical for successful delivery, rate limits
  and expected delivery failures.
- Confirm cookie name, path, max age, HttpOnly, SameSite and environment-based
  Secure behavior; confirm no credential appears in response JSON.
- Confirm CORS permits credentialed GET/POST only from the configured frontend.
- Confirm test cleanup leaves no sessions, users or OTP challenges.
- Run `docker compose config --quiet` and `git diff --check`.
- Confirm `refocus.md` retains SHA-256
  `8EE807DBC69F88F225D93D608DA7A5537FF2745454109F659342521B90849257`,
  remains untracked and is not committed.

## Out of scope

- Frontend login screens, meter/profile authorization or other protected APIs.
- Passwords, social login, refresh tokens, sliding sessions, global logout,
  session lists or account deletion.
- Production SMTP selection, proxy/TLS deployment configuration or CSRF tokens.
- Meter ledger, forecasts, dashboard, reminders or deferred automation.
- Editing or committing `refocus.md`, or modifying sibling repositories.
