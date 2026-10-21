# Task 070: Production Compose and Shared HTTPS

## Aim

Prepare a minimal production stack for monitor.roventics.com under Ticket 57.1, ready for a separately approved VPS deployment.

## Clarifications

- Domain: monitor.roventics.com.
- Follow Job Talk: internal app HTTP port 80; existing VPS Nginx owns public 80/443, redirects HTTP to HTTPS and uses host Certbot for certificates/renewal.
- Prepare files and isolated checks only. No VPS changes or new backup work.

## Change

- Add software/prod.docker-compose.yaml using existing production image targets, no reload/source mounts, health checks, restart policies and the backend's 120-second shutdown grace. Use a separate project/persistent PostgreSQL volume; initialize fresh volumes with schema.sql only, without development seeds. Never reuse/reset the development volume.
- Keep configuration minimal: one APP_DOMAIN derives the HTTPS origin; reuse existing database, OTP-secret and SMTP settings through one ignored .env per installation. Require deployment values explicitly; document URL-safe database credentials and commit no secrets. Never overwrite/copy the current development .env; leave production monthly reminders blank/off pending separate activation.
- Connect only the frontend gateway to existing external roventics_proxy under a unique Monitor alias. Keep backend/database private while retaining backend SMTP egress; publish no host ports and add no extra gateway, TLS container or renewal timer.
- Correct production Host/scheme forwarding at the trusted proxy boundary. Preserve secure cookies, relative /api routes, PATCH and other existing API methods, API error responses, assets and meter deep links; do not weaken authentication or trust arbitrary client forwarding headers.
- Add a Monitor-owned edge configuration example and concise operator instructions under software/. Verify actual DNS, proxy/network, certificate names/key type and renewal setup before any future application. Document HTTP challenge/redirect, initial certificate issuance or expansion preserving every existing domain, and reuse of renewal plus validated Nginx reload. Cover upstream DNS recovery after container replacement without breaking other sites; never blindly replace the shared proxy configuration.
- Document fresh schema-only setup and explicit DB-only first-admin assignment after normal signup, without admin env overrides or automatic role promotion. Update current context/READMEs and results. Allow up to 200 changed implementation/config lines, excluding tests/docs: Compose and its HTTPS integration form one review boundary; split further expansion.

## Reuse

- Task 036 Dockerfiles/frontend proxy, existing schema/settings/SMTP, Task 069 lifecycle and isolated checks; Job Talk's public Compose/HTTPS runbook as read-only references, not its ORM, Unix-socket gateway or app-specific settings.

## Verify

- Validate Compose with dummy settings and missing-required-value failures without printing secrets. Build/check production targets and run isolated proxy, synthetic database and captured-mail checks: schema-only initialization, persistence, HTTPS/cookie/redirect forwarding, private ports, API errors/denial, deep links and upstream replacement/recovery. Record actual checks/limits; clean only task-owned resources and leave source services/data unchanged.

## Out of scope

- VPS/DNS/firewall/proxy changes, public certificate requests, external email or reminder activation, current .env/service/data changes, data transfer, backups, sibling edits, model/UI/schema/auth redesign, new dependencies and Git publication. Ticket 57.2 covers later approved live deployment and acceptance.
