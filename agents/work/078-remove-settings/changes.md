# Task 078 results

Implemented and verified on 24 October 2026 after the user explicitly selected
removal of settings.py. No commit or push.

## Changes and reuse

- Deleted `software/backend/app/settings.py` and removed its class, imports,
  constructor arguments and FastAPI state plumbing. No replacement configuration
  class, module, compatibility shim or `.env` loader was introduced.
- Existing database, OTP, SMTP and application modules read their own environment
  variables. Reminder functions receive the UTC activation datetime and optional
  connection timeout directly. Reused the existing validators, HMAC functions,
  SMTP sender, database connection helper and reminder lifecycle/dispatch logic.
- Kept all ten required runtime values, secret-safe validation errors, persistent
  OTP key, secure-cookie rules, SMTP encryption-before-authentication, reminder
  shutdown/leases/locks and bounded worker I/O. The unrelated domain
  `ReminderSettings` remains intact. API/SQL/forecast/UI behavior is unchanged.
- Removed `pydantic-settings` from requirements. Pydantic remains for the existing
  API schemas, pinned to the running app's version 2.13.5: the first clean build
  otherwise resolved 2.14.1 and changed decimal patterns in OpenAPI. This pins an
  already-used library and does not add a dependency or model layer.
- Adapted existing tests to scoped environment overrides and primitive arguments.
  Updated active README/context guidance. Exactly two Compose files and one
  installation `.env` remain; no Docker, Nginx, database or credential edits.
- The cross-module removal exceeds the usual 100-line target, as noted in the
  prompt. Most changes remove configuration plumbing or update existing callers.

## Retirement and recovery

Dependency searches covered application imports, request state, constructors,
tests and requirements before removal. Verified byte-identical recovery copies:

- `software/backend/app/settings.py` -> `.tmp/task078/retired/settings.py`, SHA256
  `bb97a9c3fcefc9facd448c1199f1c700ed2259d5ba0ed19921543fef8cf7f832`.
- `software/backend/tests/test_settings.py` ->
  `.tmp/task078/retired/test_settings.py`, SHA256
  `ef634a0cb2150b98850fab89f13f40fc9bdef35aa1eb8849ef950c6112f315a3`.

The new runtime-boundary tests retain meaningful validation coverage without
testing the removed Pydantic settings object. Recovery metadata is in
`.tmp/task078/retirement.json`. Historical work, research and backups remain.

## Verification

- All application and test files parse; no stale settings imports/state remain.
  Both Compose modes render with one synthetic environment; production still
  has no Mailpit, and development retains its fixed mail/URL overrides.
- First fresh images built and 218 backend checks passed. Exact OpenAPI comparison
  caught only the newer Pydantic release's decimal schema patterns. No application
  behavior check failed. Read-only installed-package inspection identified the
  existing 2.13.5 version; it is now pinned. The first fixture was fully cleaned:
  four containers/four networks/one synthetic volume/two temporary image tags.
- Final pinned production images built; all 218 backend checks passed in 29.34s.
  Exact OpenAPI comparison with the running app passed. Trusted IP-SAN HTTPS,
  HTTP redirect with path/query preserved, captured OTP, secure-cookie login,
  meter rename/ledger/4 kWh-per-day forecast and logout/replay 401 all passed.
- Removed four labelled containers, four owned networks, one synthetic volume
  and two temporary image tags from the final run. Verified zero owned resources
  remain and all source development/production identities, images, runtime state,
  start times and volumes remain unchanged. Source production stays running.
- The existing .env and both certificate hashes match pre-edit values. AST,
  stale-reference, whitespace and 56 local documentation-link checks passed.

The test stack uses separate localhost ports 18480/18443/18400, labelled resources,
a fresh owned database and captured Mailpit only. Existing development AND
production container identities/state/volumes are guarded. The first-run evidence
is retained under `.tmp/task078/`; the final run is `.tmp/task078-pinned/`.
The current `.env` and certificate/key hashes are recorded in
`.tmp/task078/preservation.json`; no private values were printed.
Final evidence includes `resources.json`, `pytest.log`, `http-proof.json`,
`api-smoke.json`, `cleanup.json`, source OpenAPI snapshot and build/startup logs
under `.tmp/task078-pinned/`. These are isolated checks, not real-provider email
or a new browser/live-user acceptance run.

## Handoff

No source-service recreation, live SQL, real email, Git commit or push. The
running production backend still uses its previous image. From `software/`,
rebuild only the backend when ready:

```sh
docker compose -f prod.docker-compose.yaml up -d --build --no-deps backend
```

Provider SMTP still needs the user's real values for production email login;
this task preserves the existing `.env` and generated OTP secret.
