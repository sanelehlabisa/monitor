# Task 074: Local Production HTTPS

## Aim

Run development, local production and VPS production from one installation .env, keeping production HTTPS-only with real SMTP.

## Clarifications

- Production always uses HTTPS and real SMTP, including locally. The user supplies SMTP credentials and a unique OTP secret.
- Local certificates come from a Bash script; VPS keeps its existing Nginx/Certbot.

## Change

- Remove MONITOR_ENVIRONMENT and MONITOR_LOG_LEVEL from .env; Compose fixes the mode internally. Remove unused log-level configuration.
- Replace APP_DOMAIN with validated APP_URL for the complete public origin/CORS/gateway headers. Reject HTTP production URLs; preserve secure cookies, required settings and secret/error protections.
- Reuse FRONTEND_PORT in both Compose files. BACKEND_PORT stays development-only; production frontend port 80 and API/database remain private.
- Add an optional local-https profile: a loopback TLS proxy using the existing Nginx image. VPS disables it and keeps its shared proxy.
- Add a Bash script generating protected localhost SAN certificates in ignored software/production/certs/, refusing overwrites. Document local network setup and browser trust warnings; never change system trust automatically.
- Update the single .env/example, README/context and changes.md. Preserve credentials, SMTP values, ports and reminder cutoff; production reminders stay off.
- Permit up to 200 implementation/config changed lines, excluding tests/docs, for this cohesive TLS/configuration change; split if insufficient.

## Reuse

Existing Compose/images, Nginx, Pydantic and OTP/SMTP boundaries; no new dependency. Preserve pending Task 073 work and historical records.

## Verify

- Check all three configurations, missing/invalid settings, isolated ports and production secret/cookie rules.
- Verify certificate SANs/protection/non-overwrite behavior, Nginx and HTTPS/API/session flow using isolated resources and captured test mail.
- Verify environment/data/service preservation and cleanup. Real-provider delivery remains unverified until the user configures it.

## Out of scope

Source restarts, real email/credential changes, VPS/DNS/Certbot actions, reminder activation, database/UI/forecast changes, sibling edits, commits and pushes.
