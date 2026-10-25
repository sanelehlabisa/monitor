# Task 076: Nginx HTTPS with One URL

## Aim

Reuse Monitor's Nginx for local and production HTTPS, keeping one URL setting and exactly two Compose files.

## Clarifications

- The user approved HTTPS in Monitor's existing Nginx, reused in production.
- Use APP_BASE_URL=https://127.0.0.1:8443 locally; development keeps its Compose-local overrides, so switching modes needs no .env edits.
- Local HTTPS uses fixed loopback port 8443 in Compose, not arbitrary URL-driven port publishing. VPS public HTTPS remains on the existing shared Nginx/Certbot edge.

## Change

- Rename software/production/ to software/nginx/; update active references and ignore rules, preserving certificates, historical records and recovery copies.
- Remove FRONTEND_PORT. No backend-port variable: /api remains proxied privately.
- Add TLS port 443 to the existing frontend Nginx, published only as 127.0.0.1:8443. Retain internal HTTP 80 for the existing VPS edge; do not bind another public 80/443 listener.
- Reuse the archived certificate helper and preserved certificates for localhost/127.0.0.1 SANs. Document one-time certificate setup and self-signed browser warnings; never alter system trust or replace public Certbot certificates.
- Set the ignored .env and example to the local HTTPS URL including its port. VPS changes that URL to https://monitor.roventics.com; the same Nginx image/config remains usable.
- Preserve credentials and saved cutoff, required settings, Secure cookies, origin checks and production reminders-off. Current Mailpit/example OTP values still require one-time production credentials; do not fabricate them or claim production startup ready while missing.
- Update README/context and changes.md. Aim for at most 100 changed implementation/config lines, excluding mechanical moves and documentation.

## Reuse

Existing frontend Nginx/image, origin validation, certificate recovery copies and shared VPS proxy. No new service, dependency, profile or environment loader.

## Verify

- Validate both Compose files using the same synthetic env; check URL/port agreement, private API/DB and required settings.
- Verify rename/certificate preservation and isolated trusted-certificate HTTPS, login, meter/history/forecast and logout using captured test mail. Remove only owned test resources.

## Out of scope

Source restarts, real email, credential rotation, VPS/DNS/Certbot changes, database/UI/model changes, sibling edits, commits and pushes.
