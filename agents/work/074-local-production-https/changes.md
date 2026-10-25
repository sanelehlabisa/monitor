# Task 074 results

Approved and implemented on 23 October 2026. No commit, push or deployment.

## Changes and reuse

- Both Compose files consume one `APP_URL` from the existing ignored
  `software/.env`. Backend CORS and the production gateway use that exact
  validated origin; host/port headers are derived internally, not extra env keys.
- Removed user-managed `MONITOR_ENVIRONMENT`/`MONITOR_LOG_LEVEL` and unused
  backend log-level configuration. Compose fixes its own mode. Ten backend
  installation fields remain required; error privacy and the OTP-secret guard
  are retained. Production rejects HTTP, including localhost, and keeps Secure,
  HttpOnly, SameSite cookies.
- `FRONTEND_PORT` controls development's loopback binding or the optional
  production `local-https` profile. Production API/database stay private;
  frontend still serves internal HTTP port 80 behind a TLS edge. VPS keeps the
  existing shared Nginx/Certbot with the local profile disabled.
- Added `software/production/create-local-certs.sh` and `local-https.conf`,
  reusing the patched Nginx image and existing OTP rate-budget pattern. The Bash
  script generates ignored localhost/127.0.0.1 SAN certificates, requests private
  creation permissions and refuses existing/partial pairs. It does not change
  system trust, Docker networks, VPS certificates or settings. Exact script paths
  in `.gitattributes` retain LF on Windows.
- Updated the single example and current installation keys only. All 14 unrelated
  values, including credentials, SMTP settings, ports and saved reminder cutoff,
  have the same preservation digest. The user must supply real SMTP and a unique
  OTP secret before starting local production. Nothing silently copies provider
  credentials, enables external reminders or sends real mail.
- Updated root/component READMEs and agent context. Preserved pending Task 073
  changes, SQL/history/data, recovery files, research and historical work records.

## Retired file and recovery

Removed obsolete `software/backend/.env.example`; the active template is only
`software/.env.example`. Dependency searches found no active loader or build
consumer: Compose maps settings explicitly, Pydantic has no second env-file loader
and Docker excludes `.env*` files.

Before deletion, verified the original exactly matched Git HEAD blob
`c20a2b9f77f5a774461db354ccaacc2ad4c2fb1c` and copied it to ignored
`.tmp/task074/retired/backend.env.example`. Both 574-byte copies had SHA-256
`b3fe8a2120cfcb7823143631bcd18b1e2cf02d0fdfdada272993e2167108a622`.
Recovery is available from that copy or Git; no database/backups were deleted.

## Verification

- Both production images built using cached pinned dependency layers; frontend
  TypeScript/Vite compilation ran afresh and transformed 931 modules.
- Synthetic development, local HTTPS production and VPS Compose configurations
  passed. Twelve missing required inputs reject; local TLS is omitted when its
  profile is disabled. Private app/DB bindings and production reminders-off pass.
- Network-disabled, read-only-test-mounted backend container: **82 focused
  settings/main/CORS/auth API checks passed**. Ten missing-field application
  imports reject; actual application lifespan/health/credentialed CORS pass.
  All six installed package versions match requirements. Packaged settings SHA-256:
  `bb97a9c3fcefc9facd448c1199f1c700ed2259d5ba0ed19921543fef8cf7f832`.
- Production frontend startup accepts three canonical HTTPS origins and rejects
  17 malformed/HTTP origins. Both Nginx configurations pass `nginx -t`.
- Bash syntax and actual Git Bash certificate generation pass. SANs include
  localhost and 127.0.0.1, with CA:FALSE. A repeat refuses overwrites; both file
  hashes remain unchanged. The entire certificate directory is Git-ignored.
  Initial Git Bash absolute-output path handling was corrected before success.
- Actual optional TLS service, isolated schema-only PostgreSQL and captured
  SMTP: trusted certificate/SAN, SPA/deep link, signed-out 401, OTP login, Secure
  cookie, canonical HTTPS redirect including local port, meter create/rename,
  two readings plus one top-up, 4 kWh/day forecast, logout and subsequent 401 pass.
  No source data, real provider or external recipient was used.
- Harness-only corrections handled Compose omitting inactive services and
  schema-qualified count queries; these do not represent application failures.
- Whitespace and 56 local documentation links across eight files pass. The
  installation and single template have the same 16 unique keys; both shell
  paths resolve to Git's LF policy. Environment/certificate/evidence files remain
  ignored. This work uses the approved 200-line implementation/config exception.

Evidence/helpers remain ignored under `.tmp/task074/`: build logs, configuration
and resource metadata, `focused-checks.json`, `origin-checks.json`,
`api-smoke.json`, `cleanup.json` and environment preservation metadata.

## Preservation and limits

Exactly five owned test containers, five networks, one synthetic DB volume and
two temporary image tags were removed after identity/label checks. No owned test
resources remain. Existing Monitor container IDs/images/start metadata and volume
identities are unchanged; all four source services remain stopped as found.
Generated local certificates and recovery/evidence files remain intentionally.

Self-signed TLS requires a reviewed browser exception or manual local trust;
system trust was not changed. Windows NTFS key ACL enforcement was not verified;
the Bash script requests restrictive umask/chmod permissions. No fresh browser
flow, full test suite, real SMTP, public certificate, DNS/VPS acceptance or
whole-image security certification is claimed. Production reminders stay forced
off. Before returning a real-SMTP `.env` to development, restore Mailpit when
retaining the previously approved Mailpit-only reminder cutoff.
