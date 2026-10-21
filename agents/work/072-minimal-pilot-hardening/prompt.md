# Task 072: Minimal Pilot Hardening

## Aim

Make the existing pilot deployment simpler and address Task 071's essential gaps without adding infrastructure.

## Clarifications

- Keep one ignored software/.env and one .env.example; remove .env.production.example.
- Follow Job Talk's small deployment pattern; prioritize first users over optional improvements.

## Change

- Consolidate the examples without rewriting the real .env or changing existing development ports. Verify a recovery copy before retiring the untracked production example.
- Patch the production Nginx image. In the existing frontend gateway, reject foreign browser origins on unsafe API requests and add anti-framing headers. Preserve authenticated, headerless non-browser clients.
- Add simple per-client and aggregate OTP-request budgets to Monitor's public-edge example before client addresses are stripped. Keep policy constants in configuration, not new env settings.
- Update setup guidance/current context and record results. Aim for at most 100 changed implementation/config lines; no new service or application dependency.

## Reuse

Existing Compose wiring, APP_DOMAIN, frontend gateway, Job Talk's read-only Nginx patterns and isolated test helpers. Keep backend permissions, cookies and per-email OTP limits.

## Verify

- Validate both Compose modes with synthetic settings, build the patched image, and check Nginx configuration, headers and bounded expected rejection/rate-limit behavior.
- Use isolated captured mail and a real browser for login, meter/ledger/forecast and sign-out followed by unauthorized access. No retry of Task 071's stopped exploit probe.
- Preserve source service state/data/.env; clean only labelled test resources. Record limits, whitespace and documentation checks.

## Out of scope

New infrastructure, broad tooling upgrades/scans, UI/model/schema changes, source .env edits/restarts, real emails, reminder activation, VPS/DNS/certificate actions, sibling edits, commits and pushes. Live deployment remains separately approved.
