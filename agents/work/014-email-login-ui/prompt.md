# Task 014: Email login UI

## Aim

Complete Ticket 46 with a simple mobile-first Material UI email/OTP flow that
uses the Task 013 cookie API and honestly hands authenticated users toward their
future meter list.

## Clarifications

- Question: How should login progress? Answer: Use one compact card with an email
  step followed by a six-digit code step, plus resend and change-email actions.
- Question: How should an existing session behave? Answer: Call `/api/me` at
  startup, briefly show loading, and skip login when the cookie is valid.
- Question: What appears immediately after login? Answer: Show the normalized
  email, logout and an honest empty `Your meters` state saying meter setup is
  next; Task 015 implements the real list/create/select behavior.
- Question: What does "device" mean in active V1? Answer: A user-owned,
  nickname-only software meter/property profile, not a hardware credential or
  automated reader.
- Question: Which visual direction should be reused? Answer: Use the approved
  Switch reference's centered branding, pale background, compact white card,
  subtle shadow, clear full-width primary action and restrained black/gold cues,
  implemented natively with Material UI.
- Question: Which company artwork should be included? Answer: Copy the approved
  circular Roventics robot logo into Monitor as a local frontend asset; never
  modify the sibling repository.
- Question: How should the browser reach the API? Answer: Use relative `/api`
  requests with credentials and a Vite development proxy to `backend:8000`,
  adding no frontend environment setting.
- Question: How should future forecasting adapt? Answer: Keep one shared,
  deterministic math method and recalculate each meter's estimate whenever a new
  balance or purchased-kWh point is added. This is incremental calculation, not
  reinforcement learning or ML; new meters show `Not enough data` until real
  history supports a rate.
- Question: What persistence approach remains required? Answer: Future backend
  meter/ledger work continues with explicit raw SQL through Psycopg, never
  SQLAlchemy.
- Question: What happens to `refocus.md`? Answer: Leave it unchanged and
  untracked.

## Change

- Replace the inactive shell with a two-step controlled Material UI login flow.
- Restore the current user on load and provide clear pending, success and generic
  failure feedback without exposing backend policy details.
- Request a code, verify it, resend it, change the email and sign out through a
  small typed API client using `credentials: include`.
- Keep the six-digit code field phone-friendly and prevent duplicate submissions
  while a request is pending.
- Add the local Roventics circular logo and Switch-inspired compact visual
  treatment without copying Switch implementation code.
- Show an authenticated `Your meters` empty state without inventing meter data or
  exposing buttons that cannot work before Task 015.
- Add the Vite `/api` proxy, keep dependencies unchanged and update the HTML theme
  color to match the revised shell.
- Test API request contracts and server-rendered loading, login, code and signed-in
  states using the existing Vitest/React tools.
- Update frontend/context/roadmap documentation with the implemented login and
  clarified per-meter future flow.
- Record actual results in `changes.md`, commit and push Task 014 to `master`,
  excluding `refocus.md`, then prepare the next Task 015 scope for review.
- The UI implementation may exceed the 100-line aim because session restoration,
  both form steps and authenticated/empty states form one small usable flow; keep
  API calls separate and add no routing or state-management framework.

## Reuse

- Reuse the existing React, Vite and Material UI stack and Task 013 endpoints.
- Reuse the approved Switch layout principles rather than its HTML/CSS/JavaScript.
- Reuse the circular Roventics artwork from the approved read-only sibling brand
  source by copying it into Monitor.
- Preserve the current theme-provider/application-factory style and dependency
  set.

## Verify

- Run `npm test` and `npm run build` in the frontend container.
- Start the development stack and confirm the frontend, backend and Mailpit remain
  healthy.
- Confirm the Vite proxy reaches `/api/me`, the logo is served locally and the
  login page renders at mobile and desktop widths.
- Exercise request, code verification, restored session and logout against the
  live development services without exposing credentials in page text/storage.
- Run `docker compose config --quiet` and `git diff --check`.
- Confirm `refocus.md` retains SHA-256
  `8EE807DBC69F88F225D93D608DA7A5537FF2745454109F659342521B90849257`,
  remains untracked and is not committed.

## Out of scope

- Implementing meter/profile persistence or showing a fake device list.
- Balance/top-up entry, meter detail screens, forecast calculations, charts or
  monthly recommendations; these remain Tickets 49-54.
- SQLAlchemy, ML, reinforcement learning, default guessed usage values or stored
  forecast outputs.
- Frontend routing, global state libraries, new UI/testing packages or production
  proxy/deployment configuration.
- Hardware, OCR, MQTT, tariffs, Rand values, payment execution or automation.
- Editing or committing `refocus.md`, or modifying sibling repositories.
