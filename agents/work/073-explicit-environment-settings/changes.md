# Task 073: Explicit Environment Settings

Status: approved explicit-settings implementation, isolated verification and exact-owned cleanup complete on 22 October 2026. No source restart, real email, Git or VPS action performed.

## Context and reuse

- Read Monitor instructions/context/rules/template, software/production/backend guidance, both Compose files, settings/tests, frontend Nginx and Job Talk's read-only agent/deployment/environment contracts.
- User explicitly authorized reading Job Talk's actual .env. Inspected both real env files in memory, reporting keys/presence and local/placeholder classifications only, never secret values or copies. Both are local Mailpit configurations, not evidence of the VPS environment.
- Monitor's actual .env has 16 existing keys and lacks APP_DOMAIN; the shared example already has all 17. Production already uses internal frontend port 80 and the shared proxy on public 80/443. Job Talk's additional localhost diagnostic binding is not a requirement to publish Monitor on host port 80.
- User confirmed requiring explicit backend installation settings rather than development fallbacks while preserving existing values. No Job Talk admin/Gemini/ORM/socket architecture is proposed.
- Existing MONITOR_LOG_LEVEL is absent from production Compose and currently does not control application/Uvicorn logging. Wiring it is settings parity only, not a new verbosity feature. Production mode/reminder-off and derived URL/origin remain deliberate safeguards, not duplicate installation knobs.

## Preparation (before implementation approval)

- Master is clean at 52a0e1df39fa897305ed4f4c46de97005f78fc73: completed Tasks 070-072 were published with user approval. This new task does not include Git publication or live deployment.
- No application/config/private-env edit, source service/data action, test stack, real email, backup, sibling edit or VPS operation has occurred for Task 073. Only prompt/current-context preparation is proposed before approval.
- Independent settings-impact review confirms all 11 installation fields can be required while the optional cutoff stays off by default. Existing test imports create the app before fixtures run, so checks must receive complete synthetic environment variables before pytest/import, preserving the disposable DSN rather than adding fallback defaults or rewriting callers.
- Inspected Job Talk app/settings.py: reuse its hide_input_in_errors boundary so startup validation cannot print supplied secret values. Do not copy its development defaults, ORM or extra configuration fields.
- git diff --check and explicit whitespace checks across the three preparation documents pass. No runtime tests have run for Task 073.

## Approved implementation and reuse

- Eleven installation fields are now required in Settings: environment/log level, derived database URL/CORS origin, OTP secret and six SMTP fields. No new loader, application dependency or architecture; existing explicit Compose wiring is reused. SMTP user/password may be explicitly blank for local Mailpit, but not absent. The optional reminder cutoff still defaults off.
- Pydantic hides input values in normal validation-error text. Invalid cutoff parsing now raises a generic ISO-datetime error instead of echoing the supplied literal; this does not change accepted aware datetimes or activation behavior. Raw error dictionaries/configuration dumps are not claimed safe to publish.
- The public development OTP string is a rejection marker only, never a fallback. Production rejects blank/whitespace/example keys; existing local credentials are not rotated.
- Production Compose supplies the existing MONITOR_LOG_LEVEL and explicitly exposes internal frontend port 80. No host port is published. Production mode, reminder-off, private routing, shared HTTPS and derived database/origin values remain unchanged. Log-level wiring is parity, not new application/Uvicorn verbosity behavior.
- Added only APP_DOMAIN=monitor.roventics.com and a non-secret explanatory comment to the actual ignored software/.env. Digest checks confirm all 16 pre-existing raw values and the saved reminder cutoff are unchanged; actual/example now have the same 17 keys. No sibling credentials were copied and no private environment content was printed or archived.
- Component READMEs explain required settings, synthetic pre-import test configuration, one .env, derived values and port-80 routing. Tests remain focused on settings/startup; existing callers and sharing fixtures need no fallback layer.

## Isolated verification

- Read-only source preflight found all four existing containers exited; no source actions. Exact final backend image built with cached pinned dependencies. Its packaged settings SHA matches the final host file and all six requirement pins match; no fresh dependency resolution or unrelated upgrade.
- A file-based PowerShell metadata helper was blocked by the host execution policy before any private edit. Equivalent read-only inline metadata commands succeeded without changing that policy. This is not an application failure; the approved actual env addition passed its preservation check.
- All 33 focused settings/main/CORS checks pass. All 11 separate missing-setting eager-app imports fail clearly; invalid startup input is absent from stderr. Complete explicit settings, blank local SMTP credentials and blank/off cutoff work with real TestClient lifespan, health and credentialed CORS. Tests receive their full synthetic environment before collection, not an application fallback or source environment.
- Both Compose modes validate with synthetic settings; omission of each of 12 required production inputs fails. Custom dev ports and a synthetic saved cutoff are preserved; production mode/reminder-off stay forced, log level is explicit, frontend exposes only internal 80 and no app/DB host port is published.
- Verification runs in one labelled network-none backend container; no PostgreSQL, Mailpit, network or volume fixtures and no actual mail/DB calls. Initial harness-only Windows path/Docker-prefix corrections occurred before tests; the first run passed 33 tests/startup cases but its separate smoke script lacked /app on sys.path. That harness-only path was corrected, the first log preserved and the final full check passed. No product workaround is claimed.
- Environment preservation proof in .tmp/task073/env-preservation.json confirms exactly APP_DOMAIN added (16 to 17 keys), with all pre-existing raw values and the saved cutoff unchanged. Source credentials remain local/development; production still needs proper installation values rather than copied defaults.
- Implementation/config size is 49 changed lines: settings +24/-20, production Compose +2 and the ignored env header/domain/blank line +3. Tests/docs are excluded; no broader configuration layer was added.

## Cleanup and handoff

- Removed only one owned check container and two task backend image tags; no matching owned containers/networks/volumes remain. No DB/SMTP fixture, network or volume was created. Source IDs/statuses/images/start times/restarts/volumes match preflight and all four source services remain stopped. Base image/cache and old/new ignored evidence are retained.
- Source service/data actions, real mail, reminder activation, credential rotation, backups, sibling edits, VPS/DNS/TLS actions, commits and pushes were not performed. The only actual installation-file edit is the approved domain header/addition; all earlier values/cutoff are preserved, not falsely reported as a whole-file unchanged hash.
- Evidence: ignored .tmp/task073/resources.json, cleanup.json, focused-checks.log, focused-checks-attempt1.log, build logs, env-before.json and env-preservation.json. No source secrets, settings dumps or private config copies enter Git or chat.
- README/component/current-context guidance is updated. This is configuration/startup evidence, not a new full UI/API regression suite or live-provider/VPS validation. Prior Task 072 browser acceptance remains historical; no unrelated browser, forecasting or SQL work was repeated. Local .env still uses its existing development/Mailpit values: the VPS needs proper production secrets/SMTP values.
- Final git diff --check, explicit whitespace and all 52 relative links across eight documents pass. Actual/example env key sets match; the actual .env and ignored proof files remain excluded from Git. Only 11 expected public Task 073 paths are pending, with HEAD unchanged at 52a0e1d. Independent settings/privacy/scope review found no blocker.
