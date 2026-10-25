# Task 083 changes

## Result and reuse

- Followed Job Talk's existing shared `roventics_proxy` pattern. Monitor keeps
  three production services, serves private frontend HTTP80/loopback8082 and
  publishes no backend/database ports. Public HTTPS/redirects belong to the
  shared Roventics proxy; canonical origin, forwarded-header and write checks
  remain in the inner gateway.
- Appended the existing Monitor edge example to sibling
  `../roventics/nginx/nginx.conf`, including OTP issuance limits and ACME routing.
  Every pre-existing byte was preserved; no Job Talk or company route changed.
  This local sibling configuration edit is directly within the user's proxy request.
- Both modes initialize `000-schema.sql` then `010-users.sql`; development alone
  adds `020-demo-meters.sql`. The common seed creates the approved admin only.
  Demo memberships are scoped to the two fictional records. Plain INSERTs never
  re-promote existing users; restart never replays initialization.
- Reused existing Compose, SQL and Nginx; no application dependencies or APIs
  changed. Updated the active READMEs/context and one safe env template. The
  production guide covers deploying both repository changes, extending the
  existing certificate without dropping domains, and real SMTP acceptance.
- Retired the standalone local TLS helper and its sole .gitattributes rule after
  dependency/recovery checks. Existing ignored certificate files are preserved.

## Verification

- Both production Docker targets built successfully. Both Compose files rendered
  with one synthetic env; production has exactly three services, private port 8082,
  no backend/database host ports, admin-only seed mounts and shared-network alias.
- Fresh production: one user/admin and zero meters, balances, top-ups, sessions
  or OTPs. Fresh development: two users, one admin, two meters, four balances,
  two top-ups and no sessions/OTPs. Manual role changes survived a disposable
  database restart, proving that seeds were not replayed.
- Actual combined shared-edge and frontend configurations passed `nginx -t`.
  Isolated HTTPS probes passed HTTP redirect/path/query preservation, ACME file
  serving, company/Job Talk stub routes, unknown Host/SNI denial, SPA deep link
  delivery and unauthenticated API denial.
- Captured admin OTP/login passed through both proxies; cookie retained Secure,
  HttpOnly and SameSite. Creating a meter and its first balance yielded the
  labelled 10 kWh/day starting forecast. Canonical redirects and logout passed.
  Foreign/null-origin writes returned 403; eight bounded invalid OTP requests
  returned five 422 then three 429, while ordinary reads remained available.
- Independent configuration review found the mixed 01/010 initialization names;
  standardized them to 000/010/020 before execution. The pre-execution input guard
  detected that edit; the generated fixture was refreshed with evidence retained.
- The first fixture run passed seed/role/Nginx assertions, then its temporary HTTP
  helper shadowed Python's http module before sending a request. Corrected only
  the ignored helper and reran successfully with final configuration. First-run
  cleanup removed 7 containers, 5 networks, 2 volumes and 2 image tags; sources unchanged.
- Evidence: `.tmp/task083/retry/results.json`, `partial-results.json`,
  `startup.log`, `build-backend.log` and `build-frontend.log`. The verifier is
  `.tmp/task083/verify.py`; previous evidence remains in `.tmp/task083/`.
- Final rerun cleanup removed all 7 containers, 5 networks, 2 synthetic volumes
  and 2 image tags; no owned resources remain and source-service metadata is
  unchanged. Evidence: `.tmp/task083/retry/cleanup.json`; the earlier helper
  failure is recorded in `.tmp/task083/probe-failure.json`.
- Both repositories pass normal `git diff --check`. The existing shared proxy
  prefix and exact retirement-copy hashes were independently rechecked.
- These are HTTPS/API probes with synthetic data and captured mail, not a new
  browser walkthrough, real SMTP delivery or VPS acceptance. The test edge uses
  Monitor's patched Nginx image; the deployed shared edge's version remains unverified.

## Preservation and recovery

Dependency searches covered active Compose, Nginx, README and context references;
remaining historical seed/setup descriptions stay in historical work records and
labelled roadmap results. Retired sources are recoverable from Git commit
`eb676947b8aa0f9148b04cb04aff93004f6a554f` and verified exact-byte ignored copies:

| Retired source | Local recovery copy | SHA-256 |
| --- | --- | --- |
| `software/database/seed.sql` | `.tmp/task083/retired/seed.sql` | `b86c954f32cf50993a7526838309b7713347586e880bf33a62f6182c416cfd63` |
| `software/nginx/create-local-certs.sh` | `.tmp/task083/retired/software/nginx/create-local-certs.sh` | `9c09adf94d37f44186c2af38bce11fa75bc05a1bd559385098ef33a1f07e5920` |
| `.gitattributes` | `.tmp/task083/retired/.gitattributes` | `07a0e8f55a06ffb991bdccd9ec2a685fdf6c8700f9ac0d400fdbeefd93e8bfca` |

Proof files: `.tmp/task083/seed-recovery.json`, `tls-helper-recovery.json` and
`proxy-recovery.json`. The shared proxy's original exact copy is
`.tmp/task083/roventics-nginx.before.conf`; SHA-256
`c9f68ddaecf330b88f608f87da722323ee6a30d9dd3013874790b888598201e5`.
No current database, ignored environment, source service, certificate, research,
backup, refocus file or historical work record was edited or reset. At implementation
handoff, no VPS/DNS change, public certificate issuance, real email, commit or push
had been performed.

## Publication

The user subsequently requested committing and pushing these changes to master.
Both repositories matched origin/master before publication. The corresponding
Roventics proxy commit is `3487661ad9177d72e37f074197a3b45b77a900f1`.
The saved verification input hashes still match the implementation; private
environment files, certificates and isolated test evidence remain ignored.

## Deployment limits

The checked-in configuration now requires the shared proxy instead of standalone
local production TLS. Development remains independent. Public deployment still
requires its DNS, `APP_BASE_URL`, credentials, certificate coverage and actual
SMTP/login acceptance. The existing shared Nginx image is not upgraded by this
route-only change. Production monthly automation stays off.
