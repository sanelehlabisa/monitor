# Task 083: Shared proxy and environment-specific seeds

## Aim

Match Job Talk's shared HTTPS deployment and seed the admin in both environments without production demo meters.

## Clarifications

- Shared proxy: the user explicitly requests Job Talk's deployment pattern and setting up its proxy, including the narrow local Roventics Nginx route change.
- Seeds: both environments provision the approved admin; only development gets example meters. Existing databases remain untouched.
- Approval: the user's direct instruction to fix these two items authorizes this implementation; no unresolved design question remains.

## Change

- Join roventics_proxy as monitor-frontend; serve internal HTTP behind the shared HTTPS edge, private port 8082, with no backend host publication.
- Add only Monitor's route and OTP limits to the local Roventics Nginx configuration. Reuse existing certificate paths; document extending its domains before public use.
- Split fresh-only seeds into 010-users.sql and 020-demo-meters.sql with explicit Compose mounts.
- Retire obsolete local TLS setup after dependency/recovery checks; refresh active documentation.
- Keep these coupled configuration edits together for review even if they exceed the usual 100-line implementation target.

## Reuse

- Job Talk's external network/private HTTP pattern, Monitor's existing edge example, origin protection and PostgreSQL initialization.

## Verify

- Render both Compose files without exposing secrets; check ports, networks and seed mounts.
- Test fresh production/development initialization and shared Nginx routing with isolated synthetic resources; exercise HTTPS login and a manual meter/forecast flow where available.
- Verify recovery copies, existing route preservation, unchanged live resources and Git diff hygiene.

## Out of scope

- Live database changes, source-service restarts, VPS/DNS changes, certificate issuance, real emails, feature changes, commit or push.
