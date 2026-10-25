# Task 073: Explicit Environment Settings

## Aim

Keep Job Talk-style port-80 deployment and require explicit installation settings from Monitor's single .env.

## Clarifications

- User confirmed missing settings must fail clearly instead of using development fallbacks.
- Preserve existing credentials, SMTP settings, local ports and shared HTTPS routing.

## Change

- Remove backend installation-setting defaults and hide values in validation errors; retain the optional reminder cutoff and production-secret safety check.
- Wire the existing log-level setting into production Compose without adding a logging feature. Keep production mode and reminders-off fixed for safety, as documented.
- Add missing APP_DOMAIN=monitor.roventics.com to the ignored software/.env; preserve every existing value. Keep one .env.example and no new loader or copied Job Talk secrets.
- Make internal frontend port 80 explicit in Compose; do not bind another public host port or change the shared proxy.
- Update focused tests, README/context and changes.md; stay within 100 changed implementation/config lines.

## Reuse

Existing Pydantic settings, explicit Compose mappings, derived database URL/origin, Nginx gateway and Job Talk's read-only environment pattern. No new service, dependency or architecture.

## Verify

- Focused settings/startup checks: missing values fail without exposing secrets, supplied values work, blank local SMTP credentials remain allowed and unsafe production secrets remain rejected.
- Validate both Compose modes with synthetic settings and internal port 80; compare actual env keys and preserved-value hashes without printing secrets. Keep the real reminder cutoff unchanged.
- Use isolated checks only; preserve source services/data and keep private environments ignored.

## Out of scope

VPS/DNS/TLS actions, source restarts, real email, credential rotation, reminder activation, UI/model/schema changes, sibling edits, commits and pushes.
