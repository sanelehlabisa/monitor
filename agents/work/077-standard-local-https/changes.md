# Task 077 results

The initial launcher implementation below is historical. The later user-requested
local-only correction at the end of this record defines the current setup.

Implemented and verified on 24 October 2026. No commit, push, source-service
start/restart, source SQL, real email or VPS change.

## Changes and reuse

- `software/.env` and its single example now use exactly
  `APP_BASE_URL=https://127.0.0.1`. The VPS value is
  `APP_BASE_URL=https://monitor.roventics.com`.
- Added `software/prod.sh` as the production Compose entry point. It reads only
  the adjacent literal URL without source/eval, accepts the two agreed origins,
  handles matching quotes/whitespace/CRLF and rejects missing, duplicate or
  unsupported values. It exports that URL and derived bindings together,
  overriding inherited conflicts and fixing project `monitor-prod`.
- Local bindings are loopback HTTP80 to Nginx8080 and HTTPS443 to Nginx443.
  VPS bindings remain private TLS8443 with private HTTP8082 for the redirect.
  The existing shared VPS Nginx still owns public 80/443 and uses app-serving
  internal HTTP80; Job Talk's 8081 is untouched. VPS8082 availability remains
  an operator prerequisite, not an inspected deployment fact.
- The existing Nginx gets a small canonical 308 redirect listener on 8080,
  preserving path/query. Internal HTTP80 remains application-serving to avoid
  a shared-proxy redirect loop. TLS certificates stay read-only mounted.
- Compose requires the launcher's two internal binding variables; neither is a
  new user `.env` setting. Scope-changing override flags are rejected; ordinary
  subcommands/options remain available. Use `logs --follow`, not ambiguous `-f`.
  The launcher never changes the operator's Docker context.
- Reused the existing images, origin validator, certificate pair/helper, shared
  edge and labelled Task 076 verification pattern. Added no dependency, service,
  profile, Compose file, backend application change or schema/model/UI change.
  Exactly two Compose files and three production services remain. Development
  keeps its local ports/Mailpit and uses the same `.env` without mode edits.
- Updated six active documentation/context files and the shell LF policy.
  Task 077 changes 68 implementation/config lines including the 48-line launcher
  and the ignored URL edit; documentation/test artifacts are excluded.

## Verification actually run

- Bash syntax passed. Capture-only tests ran a copied launcher with synthetic
  adjacent settings and an asserted Docker stub, never the real `.env` or source
  Compose stack: two origins/eight valid forms, 21 invalid inputs and 25 scope
  overrides passed, including inherited URL/bind/project conflicts, another CWD,
  literal non-evaluation and CRLF. Fixed project/env/file selection passed.
  Final review added the deprecated `--workdir` directory-override alias to the
  guard after stack cleanup; all launcher checks were rerun against that final
  script, recording its hash. Nginx, images and Compose configuration are unchanged.
- Both Compose modes render with the same synthetic settings; the VPS URL-only
  variant selects private 8082/8443 rather than public 80/443. Missing inputs reject:
  eleven production settings, four development settings and two derived bindings.
  Provider URL/SMTP cannot replace development's fixed literals; production
  reminders stay off and the backend/database have no host bindings.
- Both production images built. An owned stack started with schema-only empty
  synthetic storage, actual frontend Nginx and internal captured-mail SMTP.
  No extra TLS proxy service was used.
- Actual HTTP80 returned 308 to `https://127.0.0.1` on standard TLS443, preserving
  encoded path/query without a port suffix. Internal HTTP80 returned application
  HTML/200 without a redirect, preserving the shared VPS hop's behavior.
- Trusted IP-SAN TLS, SPA deep links, captured OTP, Secure/HttpOnly/SameSite=Lax
  login/logout and canonical API redirects passed. A synthetic meter was created
  and renamed; two balances/one top-up yielded the expected 4 kWh/day forecast.
  Nginx configuration validation passed. These were API checks, not new browser
  automation or actual public VPS/SMTP acceptance.
- Removed four verified labelled containers, five owned networks, one synthetic
  database volume and two temporary image tags. Zero owned resources remain.
  All four source containers retain their exited state, IDs/images/start times,
  restarts and volume metadata. Frozen public runtime inputs are unchanged.
- Environment preservation checks confirm all eleven unrelated installation
  values/cutoff retain aggregate SHA-256
  `d7f1345bc8f82a060e554c5a13daf152b6f9f1a02399d0445606f7d031ad8cd7`.
  Certificate/key hashes still match Task 076 and the pre-edit metadata. No
  private values or keys were printed; both real/example files retain twelve keys.
- Linux script LF, whitespace, active references and documentation links pass.

Ignored evidence under `.tmp/task077/`: public `before/` snapshots,
`env-before.json`, `launcher-proof.json`, `resources.json`, `http-proof.json`,
`api-smoke.json`, `cleanup.json` and configuration/build/startup logs. No retired
source files were deleted; historical work, backups, research and recovery copies
remain untouched. Only synthetic test resources were removed.

## Operator handoff and limits

From `software/`, after initial credentials/certificate/network setup, use:

```sh
bash prod.sh config --quiet
bash prod.sh up -d --build --wait
```

Local HTTP80/HTTPS443 must be free; do not stop unrelated services to claim them.
The real `.env` still contains Mailpit/example OTP values, so the user must supply
real SMTP and a unique OTP secret before production startup. Local self-signed
TLS still gives a browser warning unless explicitly trusted. VPS public Certbot
certificates remain separately managed; no system trust, VPS or credential change
was performed. Production reminders remain off. Nothing is committed or pushed.

## User-requested local-only correction, 24 October 2026

The user rejected the launcher and explicitly requested direct Compose, then
clarified that only local production matters now: frontend HTTP80/HTTPS443 and
backend8000. This is a correction to Task077, not a new deployment task.

- Read sibling `../roventics/docker-compose.yaml`, `dev.docker-compose.yaml`,
  Nginx configuration and README, plus Job Talk's production/development Compose
  and public example. Reused their direct Compose pattern; no sibling edits or
  private environment reads/copies.
- Removed `software/prod.sh` and `software/frontend/15-app-origin.envsh`.
  The certificate generator `software/nginx/create-local-certs.sh` is the only
  active application shell script. Nginx's built-in template substitution and
  a small map derive the upstream host from the configured origin; backend
  canonical-origin validation remains unchanged.
- Both Compose files read the single existing `.env`. Every interpolated
  installation key is present in that file and the example; twelve keys match.
  No binding variables remain. Development retains fixed local/Mailpit overrides.
- Production publishes only loopback frontend80/443 and backend8000, keeps the
  database unpublished, and has exactly three services with no Mailpit. HTTP80
  redirects to HTTPS443; removed the obsolete8080 listener. Frontend health uses
  internal HTTPS with the self-signed certificate. Compose creates its own
  networks; there is no external `roventics_proxy` prerequisite.
- The two modes share backend8000, so run one mode at a time. Production
  reminders remain off. All twelve previous environment assignments, both
  certificate files, data, research and historical work remain unchanged.
- Updated the six active READMEs/context files, shell LF policy and this prompt
  amendment. VPS work is deferred; old shared-proxy notes are explicitly
  historical and require adaptation before any future deployment.

### Retirement and recovery

Dependency searches identified the launcher commands, Compose error messages,
Dockerfile hook and LF entries, which were replaced/removed. Before deletion,
verified byte-identical ignored recovery copies:

- `software/prod.sh` -> `.tmp/task077-direct/retired/prod.sh`, SHA-256
  `b48b78a0816ed855789c4c8fbce8164220f9e57e57d7dfd36c447e051e385a28`.
- `software/frontend/15-app-origin.envsh` ->
  `.tmp/task077-direct/retired/15-app-origin.envsh`, SHA-256
  `32ea59d1fce5387cb72669f5f96869ae7686f2ade0c242e9900eeae181fc6370`.

Exact paths and hashes are in `.tmp/task077-direct/retirement.json`. Certificates,
keys and recovery artifacts remain ignored. Prior work records were preserved.

### Verification of the final local configuration

- The user's direct commands, `docker compose -f prod.docker-compose.yaml config
  --quiet` and the development equivalent, both pass with the actual `.env`,
  without a wrapper or shell-exported binding values. Rendered secrets were not
  printed. Read-only validation reported sandbox Docker-config access warnings,
  but both commands returned zero; isolated runtime checks used approved access.
- Both modes render from one synthetic environment. Checked fixed ports, all
  example keys, development mail overrides, no external network, no profiles,
  two Compose files, production's three services and certificate-only script.
- Both production images built. The isolated stack passed fresh-schema startup,
  Nginx validation, trusted loopback TLS and the actual HTTP80-to-HTTPS443 redirect
  with encoded path/query preserved. Backend localhost8000 `/health` returned200.
- Captured OTP, Secure/HttpOnly/SameSite=Lax login/logout, SPA deep links,
  canonical API redirects and meter create/rename/ledger/forecast passed.
  Two balances plus a top-up produced the expected4kWh/day rate. This was an
  API flow with synthetic data/captured mail, not real-provider/browser acceptance.
- Test-only Mailpit was added only to the ignored isolated fixture, not production
  Compose. Its networks disable masquerading and use an isolated trusted subnet;
  actual production credentials and source databases were never used.
- Removed exactly four labelled containers, four networks, one synthetic volume
  and two image tags; verified zero owned resources remain. All source container
  identities/state/start times/volumes remained unchanged. Runtime input hashes
  were stable throughout. Environment/certificate preservation and ignored-file
  checks passed. Whitespace and56local documentation links passed.

Evidence: `.tmp/task077-local/resources.json`, `http-proof.json`, `api-smoke.json`,
`cleanup.json`, `preservation-result.json` and build/startup logs. An earlier
direct-Compose preparation was superseded by the user's local-only clarification:
its two built image tags were removed before proceeding, with no containers or
volumes started; see `.tmp/task077-direct/cleanup.json`.

### Current command and remaining setup

From `software/`, use `docker compose -f prod.docker-compose.yaml up --build`.
Open `https://127.0.0.1`; backend health is `http://127.0.0.1:8000/health`.
The actual `.env` still has Mailpit SMTP and the public example OTP secret, so
the user must supply real SMTP and a unique OTP secret before source production
startup/login. This fix does not rotate credentials or send real mail. Existing
certificates are reusable; no generation/startup wrapper is required now.
Nothing was committed or pushed, and source services were not started/restarted.

## Follow-up startup repair, 24 October 2026

The user then ran production and reported `Production requires a unique
MONITOR_OTP_HMAC_SECRET`. Read-only inspection found the production database
healthy, backend restarting and frontend created. The user's request to repair
that failed startup authorized the following limited recovery:

- Replaced only the known public example OTP secret in ignored `software/.env`
  with a cryptographically random 256-bit value. The value was never printed or
  committed. Verified all other environment bytes remained unchanged. Existing
  custom secrets would have been preserved by the guarded edit.
- Recreated only the failing backend with direct Compose `up -d --no-deps --wait
  --wait-timeout 60 backend`, then started its already-created frontend likewise.
  Both became healthy. Verified database ID/start time/mounts unchanged; no SQL,
  seed replay, volume reset, real email or development-service change occurred.
- Read-only checks passed: HTTP80 redirects308 to configured HTTPS, trusted
  IP-SAN HTTPSroot200, signed-out `/api/me`401 and backend8000 `/health`200.
  A temporary check first had a local variable shadowing the HTTP module; fixed
  the verification command and reran successfully. No application change was
  necessary for that test-command error.
- No validation or login protections were removed. `settings.py` supplies shared
  database/SMTP/cookie/reminder configuration; the broader cleanup choice was
  asked separately. This repair changes private configuration and runtime state,
  not application code. SMTP is still Mailpit and requires real provider values
  for production email login; no provider acceptance is claimed.
- Updated active context/local setup guidance. Prior no-start/no-rotation notes
  describe the earlier isolated verification, before this explicit repair request.
  No commit or push was performed.
