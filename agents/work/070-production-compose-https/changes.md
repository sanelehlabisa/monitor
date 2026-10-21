# Task 070: Production Compose and Shared HTTPS

Status: approved on 20 October 2026; implementation, isolated verification and owned-resource cleanup complete. Ticket 57.1 is complete; no live deployment or Git publication authorized.

## Context and reuse

- User confirmed monitor.roventics.com and reuse of the existing VPS Nginx/host Certbot pattern, with Monitor HTTP on internal port 80 and public HTTPS on 443.
- Read Monitor agent instructions/context/rules/template, relevant software/database/backend/frontend guidance, production image/proxy/settings/auth/SMTP code and public configuration examples. No private environment or certificate contents were inspected.
- Job Talk reference inspection was read-only: prod.docker-compose.yaml, nginx/app.conf.template, scripts/production-preflight.sh and docs/production-operations.md. Its existing public proxy owns 80/443; external roventics_proxy connects its HTTP gateway, while host Certbot owns issuance/renewal. Actual VPS state was not checked.
- Reuse Monitor's existing built frontend as gateway; do not copy Job Talk's extra Unix-socket architecture, SQLAlchemy/admin settings or restrictive method list, which would exclude Monitor PATCH operations.
- Task 069 is committed/pushed to master as 0d029aef62825be810a8ff7674bffd93e97a2025. Remote SHA and clean worktree were verified before this preparation.

## Planned boundary

- Ticket 57.1 / Task 070 prepares production files, minimal explicit configuration, a shared-edge example/runbook and isolated checks. The user approved its 200-line implementation/config exception and isolated checks, not source/VPS actions.
- Ticket 57.2 retains live DNS/proxy/certificate/SMTP deployment and end-to-end acceptance as separately approved work. Production monthly automation stays disabled until an explicit saved activation decision.
- No new backup project, source restart/reset/environment edit, external mail, certificate request, sibling modification or Git publication is included.

## Preparation checks

- Independent read-only scope review found no clarification blocker; incorporated trusted HTTPS/redirect headers, SMTP egress, separate installation settings, manual first-admin onboarding and upstream DNS/replacement recovery into the proposed checks/instructions.
- git diff --check, explicit whitespace checks and all 25 relative links across the five preparation documents pass. Worktree changes are limited to those documents; no implementation/configuration or private environment files changed.
- Documentation-only preparation; implementation, image builds, Docker/SMTP/database checks and live deployment have not run for Task 070.

## Implementation and reuse

- Added the three-service production Compose and blank-secret production example. Existing pinned production targets, numeric backend user, fresh SQL schema and SMTP boundary are reused; no dependency, model, API, UI, auth or SQL change.
- Production owns a separate project/volume and mounts schema only, never development seeds. Backend/database publish no ports; only frontend joins existing roventics_proxy as monitor-frontend. Backend has separate SMTP egress. Fixed private web subnet and Uvicorn trusted CIDR match; the operator guide requires a collision check before deployment.
- Production forces monthly activation empty regardless of inherited development settings. No current .env edit or local cutoff copy. A single APP_DOMAIN derives origin/canonical Host. Frontend template substitutes only APP_DOMAIN, not Nginx variables.
- Both proxy hops resolve Docker upstreams at request time, preserve URI/query/methods and replace client forwarding headers with configured HTTPS identity. Internal API Uvicorn trust is restricted to the private web CIDR. No second gateway, certificate service or renewal timer.
- Added Monitor-only edge examples and an operator guide covering verified DNS/mounts, HTTP bootstrap, certificate SAN/key-type preservation, existing Certbot timer/hooks, first verified signup/manual DB admin and later live acceptance. No commands in that guide were run against the VPS.
- Routine Monitor-only production access logs are disabled to avoid query-email logging; error/application logs remain private and may contain URIs. Other sites' logging is untouched. Independent read-only config/runbook review found no blocker.

## Isolated verification

- Dummy production Compose validation passes; omitting each of its 11 required deployment values fails. All three services publish no host ports, fresh DB mounts only schema, and production activation stays empty even with an inherited nonempty development cutoff.
- Both public Dockerfile production targets build successfully. An intentionally network-disabled first backend attempt failed on an unavailable pip cache/DNS; one default-network retry succeeded. Successful builds reused cached pip/npm-ci dependency layers, not a fresh dependency resolution/install. The frontend executed TypeScript/Vite build: 931 modules, 1.69 seconds, with the existing >500 kB chunk warning. All six backend installed pins were verified exact.
- The owned, all-internal six-service verification stack used a synthetic PostgreSQL DB/Mailpit, built production backend/frontend, local self-signed TLS edge and probe. Fresh schema had nine domain tables and zero users/meters/balances/deliveries: no seed replay.
- Real local HTTPS and captured OTP login passed, including Secure/HttpOnly/SameSite cookie, HTTP redirect/challenge, assets/deep links, API JSON/errors/denial, forged forwarding-header sanitization, untrusted direct proxy-header rejection, CORS, meter creation/PATCH/search, balance/top-up entries, forecast and purchase deletion. Logout/revocation passed after persistence phases.
- Backend and frontend replacements were forced onto different IPs while owned holder containers reserved the old addresses. Both recovered through runtime Docker DNS without replacing the edge; PostgreSQL restart and recreation retained the synthetic account/session/meter/history. Exact phase evidence is in ignored .tmp/task070/resources.json. Runtime checks also verified Nginx 1.30.5, backend UID/GID 10001, no reload and disabled access logs.
- The first probe stopped before any user data because a Windows-generated challenge file had CRLF while the test expected LF. The fixture assertion was corrected to tolerate line endings and the same owned stack resumed; no product-code fix, source action or hidden retry was involved.
- Final cleanup at 06:19:31 UTC removed six current owned containers, four internal networks, one synthetic PostgreSQL volume and two task image tags. Five earlier replacement/holder containers were already removed and recorded. No matching task resources remain; base images/build cache are retained. Temporary synthetic data is reproducible through the ignored helpers; no live data was removed.
- Final source IDs/images/start times/restart counts/volumes, ignored .env digest and frozen public input hashes are unchanged; all four source services were healthy at the sampled checks. No source SQL, login/mail/service action or live proxy-network connection occurred. Evidence: ignored .tmp/task070/resources.json (verified-cleaned), cleanup.json and build logs.
- Runtime/config review size is 149 changed lines against the approved 200-line exception. Final git diff --check, explicit whitespace, the 14-public-path allowlist and all 54 relative documentation links pass. No full backend/frontend regression suite was rerun: application code/UI/schema are unchanged; Task 069's 157/43 checks remain historical baseline, not newly claimed results.

## Handoff and limits

- Ticket 57.1 is complete; root roadmap/current component guidance/context are updated. Ticket 57.2 remains open for separately approved live deployment and real-user acceptance.
- Verification used local self-signed TLS and anonymous isolated SMTP. Real provider TLS/auth/email, DNS, VPS proxy configuration, public certificate issuance/renewal and household/browser usability are not verified. No .env/source data changes, backups, sibling edits, commits or pushes were performed.
