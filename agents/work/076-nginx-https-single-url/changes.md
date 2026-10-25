# Task 076 results

Implemented and verified the approved scope on 23 October 2026. No commit,
push, source-service start/restart, source SQL, real email or VPS change.

## Changes and reuse

- Renamed `software/production/` to `software/nginx/`, updating active links,
  ignore rules and LF policy. Historical work records remain unchanged.
- Existing frontend Nginx now listens on HTTP80 and HTTPS443. Production binds
  only `127.0.0.1:8443:443`, mounts certificates read-only and retains HTTP80
  for the existing shared VPS edge. Backend/database remain private.
- Both the ignored `.env` and single example use
  `APP_BASE_URL=https://127.0.0.1:8443`; removed `FRONTEND_PORT`. No backend
  port setting is needed because `/api` stays proxied. The TLS host binding is
  fixed, not an arbitrary URL-to-port parser.
- Exactly two Compose files remain. Development keeps fixed local ports and
  captured Mailpit settings, so a properly configured production `.env` also
  works with development without edits. VPS public origin becomes
  `https://monitor.roventics.com`; shared Nginx/Certbot still owns public HTTPS.
- Restored the small certificate helper from the verified Task 075 recovery
  copy, changing only its private-certificate guidance. Reused the preserved
  certificate pair, existing images, origin validation and cookie/proxy settings.
  No service, dependency, profile, app UI/model or database change was added.
- Production reminders remain off. Updated current READMEs/context; pending
  Tasks 073-075 and unrelated work are preserved. Configuration/helper changes
  remain below the approved 100-line aim, excluding docs and mechanical moves.

## Preservation and recovery

Before the native directory move, resolved both absolute paths and checked they
were the exact intended source/destination within this workspace. Dependency
searches identified the active links/ignore entries. Immediately after the move,
all four original file hashes matched, and the old directory was absent.
The moved README was subsequently updated as documentation; the edge example
and both certificate files still match their pre-move hashes.

| Preserved file under `software/nginx/` | SHA-256 |
| --- | --- |
| `monitor-edge.conf.example` | `a3ee98501f8e244545ae666269f7ad6dfb10674bdc94732b7c511544d46707f8` |
| `certs/localhost.pem` | `effa75d1a53b7180df5ece0bcea123659df5d5dbcbe1539fc58e3121250fc237` |
| `certs/localhost-key.pem` | `4ea758d4d5d17c51d7140628f364e4affb31fb962866c3f79ff061255e924e90` |

The helper's exact recovery source remains
`.tmp/task075/retired/create-local-certs.sh`, SHA-256
`189156c00d26e11564b0b25c523e71bd3c61b370806e07a25698271478328338`.
Task 075's retired overlay/config copies remain untouched. No unique design
sources, live records, backups, research or historical work records were deleted.

All eleven other installation values retain their original aggregate SHA-256:
`d7f1345bc8f82a060e554c5a13daf152b6f9f1a02399d0445606f7d031ad8cd7`.
Credentials, SMTP and saved cutoff were not changed. The real/example files
retain the same twelve keys; `.env`, certificates and test evidence are ignored.

## Checks actually run

- Both production images built. Same synthetic settings render both Compose
  modes; a URL-only VPS variant also passes. Production has exactly three
  services, no profiles, only loopback TLS8443 and no public database/API.
- All eleven missing required production settings and all four missing required
  development settings reject. Minimal development PostgreSQL/OTP settings pass;
  provider URL/SMTP values cannot replace development's local literals.
- A labelled isolated stack started with fresh schema-only storage and no seeded
  users/meters/reminders. It used the actual frontend TLS listener on port 8443,
  owned networks, read-only source mounts and captured mail; no extra TLS service.
- Trusted-certificate IP-SAN HTTPS, SPA deep link, captured OTP, Secure/HttpOnly/
  SameSite cookie login/logout and canonical HTTPS-port redirect passed.
  Synthetic meter creation/rename, two balances, one top-up and the expected
  4 kWh/day forecast passed. Nginx configuration validation passed.
- Bash syntax passed; the helper refused to overwrite the existing pair, whose
  original hashes still match. A separate ignored helper copy generated a valid
  localhost/127.0.0.1 SAN certificate with CA:FALSE; IP verification passed.
  This does not install system trust or prove Windows NTFS key ACL protection.
- Removed exactly four labelled test containers, five owned networks, one
  synthetic database volume and two temporary image tags. Zero owned resources
  remain. Removed the two fixture-generated certificate/key files after testing;
  the original certificate pair is untouched. All four source containers retain
  their stopped state and original
  IDs/images/start times/restarts/volume metadata; no source data was queried.
- Active documentation links and whitespace checks pass. Final review found no
  stale active path/port guidance; historical results remain clearly separated.

Ignored evidence: `.tmp/task076/rename-proof.json`, `env-before.json`,
`resources.json`, `api-smoke.json`, `cleanup.json`, configuration/build/startup
logs and the certificate-helper fixture. Test helpers did not read the real
`.env`; separate preservation checks compared hashes without printing values.

## Remaining operator prerequisites

The actual `.env` still has Mailpit/example OTP values. Supply real provider SMTP
and a unique OTP secret once before production startup; switching dev/prod then
needs no `.env` edits. The private certificate pair and shared proxy network must
exist on each installation. Local self-signed TLS has a browser warning; the same
private pair on a VPS never replaces its public Certbot certificates.

No new browser automation, real SMTP delivery, public DNS/TLS, VPS deployment or
complete security certification is claimed. Source services remain untouched.
