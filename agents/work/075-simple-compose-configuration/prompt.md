# Task 075: Simple Compose Configuration

## Aim

Keep production settings in one .env, with local development overrides only in Compose and no profiles.

## Clarifications

- Production's base URL includes HTTPS but no port: APP_BASE_URL=https://monitor.roventics.com. Local production uses https://localhost and its separate FRONTEND_PORT.
- Development Compose may fix local URLs, ports and Mailpit settings; do not add backend configuration defaults.
- The user approved a small local HTTPS Compose override instead of profiles. VPS keeps its existing Nginx/Certbot.

## Change

- Replace the public APP_URL key with APP_BASE_URL and remove COMPOSE_PROFILES and all active profile directives.
- Fix localhost URLs, development ports and Mailpit SMTP/sender values in dev Compose. Keep database credentials and OTP secret explicit; preserve existing data and credentials.
- Keep prod Compose driven by .env for production settings and real SMTP, with required values and HTTPS validation unchanged. API/database stay private; reminders stay off.
- Move the local TLS service into local.https.docker-compose.yaml. The explicit local command combines it with prod Compose, using the existing certificate script and a nondefault loopback FRONTEND_PORT such as 8443. Both gateway and backend receive the same derived HTTPS origin.
- Remove now-unused development-only port keys from .env/example. Preserve all other values and the saved reminder cutoff; never rotate or copy secrets.
- Update README/context and changes.md; preserve Tasks 073/074 records and pending work. Aim for at most 100 changed implementation/config lines.

## Reuse

Existing Compose/images, TLS config/certificate script, origin validation and SMTP boundary. No new dependencies or configuration loader.

## Verify

- Validate development, VPS and local HTTPS configurations without profiles; development must ignore production URL/SMTP settings.
- Check matching local origins/ports, private production services, missing required settings and preserved values. Use isolated HTTPS/API/session checks and captured test mail only; remove owned test resources.

## Out of scope

Source restarts, data/schema changes, real email, credential rotation, VPS/DNS/Certbot changes, reminder activation, UI/model changes, sibling edits, commits and pushes.

## Developer amendment during implementation

The user superseded the local-HTTPS override approval: keep exactly two Compose
files, no profiles and no app-owned local TLS; follow Job Talk's inspected shared
Nginx/Certbot pattern. Production settings remain in .env, with a loopback HTTP
frontend diagnostic binding. Public production HTTPS still comes from the existing
edge; standalone local HTTPS is not supplied or claimed. Archive abandoned local
TLS sources before retirement and preserve generated certificates/history. This
adds deletion-only cleanup beyond the original small configuration edit; do not
add new TLS infrastructure or silently weaken Secure cookies.
