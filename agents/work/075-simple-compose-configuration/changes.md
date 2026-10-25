# Task 075 results

Implemented the developer-amended two-file configuration on 23 October 2026.
No commit, push, source restart or VPS change. Final Compose checks pass;
fresh end-to-end acceptance is incomplete.

## Scope correction and reference evidence

The developer explicitly cancelled the extra local HTTPS Compose file during
implementation. That instruction supersedes the earlier overlay/profile plan.
Read-only inspection of the actual sibling Job Talk repository confirmed:

- `job_talk/prod.docker-compose.yaml` requires installation values from `.env`,
  derives HTTPS public origins and publishes only a loopback HTTP gateway port.
- `job_talk/nginx/app.conf.template` listens on internal port 80, not a local
  TLS listener. `job_talk/docs/production-operations.md` documents the existing
  shared Nginx/Certbot edge owning public ports 80/443.
- Job Talk does not supply standalone local production HTTPS. Monitor must not
  claim that capability or silently downgrade Secure production cookies.

## Final changes and reuse

- Exactly two active Compose files: `software/dev.docker-compose.yaml` and
  `software/prod.docker-compose.yaml`. No profiles, third Compose file or
  application-owned local TLS service.
- `.env` holds `APP_BASE_URL=https://monitor.roventics.com`, without a port.
  Production uses its explicit database/OTP/SMTP values. Internal frontend
  `APP_URL` and backend CORS are derived from that base; no second public URL key
  or Python configuration fallback was added.
- Production frontend exposes internal HTTP 80 to the existing shared edge and
  binds `127.0.0.1:${FRONTEND_PORT}:80` for diagnostics, following Job Talk's
  loopback pattern. This port is not the public HTTPS origin or an HTTP login
  alternative. Database/API have no host bindings; production reminders stay off.
- Development fixes localhost ports 5173/8000/5432, Mailpit SMTP 1025, blank
  capture credentials and local sender directly in Compose. Production URL/SMTP
  settings cannot override those literals. Database credentials and OTP secret
  remain explicit; the saved reminder cutoff stays captured-mail-only.
- Removed public `APP_URL`, `COMPOSE_PROFILES`, `BACKEND_PORT` and `POSTGRES_PORT`
  keys. All twelve retained installation values, including credentials, SMTP,
  selected frontend port and saved cutoff, retain the preservation digest.
- Updated the single safe example, six current READMEs/context files and the
  prompt amendment. Preserved pending Tasks 073/074 and historical work records.
  Reused existing images, Nginx origin validation, SMTP/OTP boundaries and
  development reload; no backend/frontend application code or dependencies changed.
- The initial small configuration edit was within its 100-line aim. The explicit
  developer correction additionally retires 57 lines of abandoned TLS script/config
  and its policy entry; this deletion-only cleanup is recorded rather than hidden
  as implementation of the now-cancelled overlay.

## Retired sources and recovery

Dependency searches showed the local TLS configuration was referenced only by
the rejected overlay, and the certificate script only by its LF policy entry.
No Dockerfile or either final Compose file consumes them. Before deleting, copied
each exact source to ignored `.tmp/task075/retired/` and verified equal SHA-256:

| Retired source | Recovery filename | Bytes | SHA-256 |
| --- | --- | --- | --- |
| `software/local.https.docker-compose.yaml` | `local.https.docker-compose.yaml` | 757 | `c3523d6619c63a7337432bfa46a4120f2aa47d4940bacc3fa335e87bff999a29` |
| `software/production/create-local-certs.sh` | `create-local-certs.sh` | 1167 | `189156c00d26e11564b0b25c523e71bd3c61b370806e07a25698271478328338` |
| `software/production/local-https.conf` | `local-https.conf` | 1148 | `0ae846c0e15aa0c52aa522c3b51c0b1f9b09db7cdff127ab285c7dccf77abfdf` |

These sources were uncommitted; recovery is from the verified copies, not a
claimed Git commit. Generated private certificates remain ignored and untouched.
No source data, backups, research or historical work records were removed.

## Checks and limits

- Final two-file-only validation passes: exactly two Compose files, no profiles,
  production env mapping, fixed development Mailpit/ports, matching public
  gateway/CORS origin, frontend loopback-only binding and private backend/database.
- All twelve required production inputs reject omission. Development starts its
  configuration with only explicit PostgreSQL/OTP settings; all four missing
  required development values reject. Provider URL/SMTP values are ignored by
  development. Saved cutoff preservation and production reminders-off pass.
- Final environment/template checks pass with thirteen matching keys and twelve
  unchanged retained values. Whitespace and 56 local links across eight current
  documentation/work files pass.
- Both production images built with pinned cached dependency layers during the
  earlier verification attempt. The rejected local TLS fixture then exceeded its
  bounded 100-second startup wait before API/login checks. No fresh end-to-end
  pass or proven root cause is claimed, and historical Task 074 results are not
  relabelled as current readiness.
- Exactly five owned containers, five networks, one synthetic test volume and
  two temporary image tags were removed after identity/label checks. Zero owned
  resources remain. All four source containers retain their stopped state and
  identity/image/start/volume metadata; no source SQL, login or email was performed.

Evidence remains ignored under `.tmp/task075/`: `two-file-checks.json`,
`cleanup-aborted.json`, `retirement-proof.json`, environment hash metadata,
before/configuration snapshots and build logs.

Real SMTP, public TLS/DNS/VPS state, browser/household acceptance and standalone
local production HTTPS are not verified. The final app expects an already
configured external HTTPS proxy, just like the inspected Job Talk setup.
