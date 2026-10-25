# Task 077: Standard Local HTTPS

## Aim

Local HTTP80 redirects to HTTPS443; preserve the shared VPS proxy.

## Clarifications

- Local: APP_BASE_URL=https://127.0.0.1.
- VPS: APP_BASE_URL=https://monitor.roventics.com.
- VPS public 80/443 already belong to shared Nginx. A small launcher will select
  bindings from this URL; plain Compose cannot make that conditional selection.

## Change

- Add software/prod.sh as the production Compose entry point. Read only
  APP_BASE_URL without source/eval; reject missing, duplicate or unsupported
  values. Export the validated URL and derived bindings together so inherited
  shell values cannot disagree. No new user .env settings or dependencies.
- Local bindings: 127.0.0.1:80 to redirect listener8080; 127.0.0.1:443 to TLS443.
  VPS bindings: private HTTP8082 and existing TLS8443, preserving public 80/443
  and Job Talk's 8081. VPS8082 availability requires an operator check.
- Existing Nginx gets the redirect listener, preserving path/query. Retain
  internal HTTP80 serving for the VPS proxy to avoid redirect loops.
- Update .env, example, active docs/context and launcher commands. Keep two
  Compose files, three production services, private API/DB, existing credentials,
  certificates and reminders-off. Aim for at most 100 implementation lines.

## Reuse

Existing Nginx/image, certificate pair/helper, origin validation, VPS edge and
labelled isolated test helpers.

## Verify

- Launcher syntax/input checks; synthetic local/VPS/dev configuration checks.
- Isolated HTTP80-to-HTTPS443 redirect, trusted certificate, captured OTP,
  meter/history/forecast and logout; verify internal HTTP80 has no redirect loop.
- Preserve source metadata and credential/certificate hashes. Do not stop other
  services if ports are occupied. Clean owned fixtures; record changes.md.

## Out of scope

Source starts/restarts, real mail, credential rotation, VPS/DNS/Certbot changes,
sibling edits, database/UI/model changes, commits and pushes. Actual SMTP/OTP
placeholders still need user setup; no browser trust or deployment certification.

## User-requested correction, 24 October 2026

The user rejected the launcher after direct Compose reported missing binding
variables and explicitly requested a fix using the sibling Roventics/Job Talk
pattern. This amendment replaces the launcher scope above: direct development
and production Compose, one shared `.env` with every installation variable
documented/present, development-only overrides/Mailpit, and only the certificate
generator as a shell script under `nginx/`.

Read both sibling implementations without modifying them. Keep local public
origin `https://127.0.0.1`; put the existing HTTP/HTTPS binding variables directly
in `.env`/example (loopback80/443). Document private loopback8082/8443 plus the
domain URL for the shared VPS, whose public80/443 already belong to Roventics.
Remove `prod.sh` and the custom origin shell hook after verified recovery copies;
use a small Nginx map and its built-in template support for upstream authority.
Preserve origin validation, internal HTTP80, certificates, secrets and all data.
Update active guidance; retain the original prompt/results as historical evidence.
Verify direct configuration and isolated HTTPS/API behavior, then clean only
owned fixtures. Existing out-of-scope boundaries remain in force.

The user then clarified that only local production is in scope: frontend HTTP80
redirecting to HTTPS443 and backend localhost8000, with VPS work deferred.
This supersedes the binding-variable proposal immediately above. Use literal
loopback bindings in production Compose, remove those extra `.env` keys and the
external shared-network prerequisite. Compose creates its own frontend ingress
network. Preserve the sole local `APP_BASE_URL=https://127.0.0.1` setting and the
development overrides. Verify local direct startup with isolated data/captured
mail; preserve source services. Public deployment needs later separate changes.
Remove the now-unused8080 listener: frontend HTTP80 redirects and TLS443 serves
the app. Its internal health check uses HTTPS with the local self-signed certificate.
