# Task 072: Minimal Pilot Hardening

Status: approved implementation, isolated verification and owned-resource cleanup complete on 21 October 2026. Ready for review and the separately approved VPS setup/acceptance step; no source service/VPS/Git actions performed.

## Context and reuse

- Read Monitor instructions/context/rules/template, relevant READMEs, both Compose files, settings/auth boundaries, production Dockerfile and proxy examples, and Task 071's findings.
- User confirmed one real ignored software/.env plus one .env.example, retiring .env.production.example. Both Compose files already use the same actual .env; no extra dotenv loader or wholesale env_file wiring is necessary.
- Job Talk inspection was read-only: agent guide, deployment/environment guidance, Compose, gateway template and Dockerfile. Reuse only small configuration patterns, not its extra gateway/socket architecture, admin settings or ORM.
- Proposed scope is production Nginx patch/origin/framing policy and public-edge OTP budgets, retaining existing authentication/authorization and application behavior. No new service/dependency/env policy knobs; no earlier stopped exploit-probe retry.

## Preparation and preservation

- Existing Task 070/071 edits are uncommitted and preserved. The next work number is 072; roadmap IDs remain unchanged.
- The production example is untracked, so Git is NOT a recovery copy. Before approved retirement, verify an exact local archival copy. Active links are in software/README.md and software/production/README.md; old ignored Task 070/071 hash helpers remain historical artifacts.
- Before approval, no implementation, private environment inspection/edit, source service/data action, test stack, image build, real mail, VPS action or Git publication occurred. The following preparation check is not a runtime result.
- Independent read-only scope review found no substantive gap. git diff --check and explicit whitespace checks across the three preparation documents pass; no runtime checks are claimed.

## Approved implementation

- Existing frontend serving image changes from Nginx 1.30.5 to 1.30.6, in the fixed range of the [vendor advisory](https://nginx.org/en/security_advisories.html). No backend/npm package or extra image/service is added.
- Existing gateway checks POST/PUT/PATCH/DELETE API requests for a present foreign/null Origin or same-site/cross-site Fetch Metadata; only the configured HTTPS origin is allowed when Origin is present. Headerless non-browser clients remain compatible and still require backend authentication/authorization. This is a browser write boundary, not client identity.
- X-Frame-Options DENY and CSP frame-ancestors 'none' apply to gateway responses including errors. No broad CSP/asset/font/layout redesign.
- Public-edge example has two Monitor-only OTP issuance budgets: 10 requests/minute per connection IP with burst 5, and 60/minute aggregate with burst 10; excess returns 429 immediately. Keys are empty for other endpoints, policy stays in configuration, and client identity is evaluated before proxy headers are stripped. No new forwarded-IP trust, Redis or tuning env variables.
- Actual .env and existing dev ports/settings remain untouched. Source service state/data and pre-existing Task 070/071 work are preserved; exact archive and verification results follow after checks complete.

## Environment consolidation and recovery

- software/.env.example is the sole active example; APP_DOMAIN is its only added key. Existing development values, ports and saved-cutoff setting are preserved. Production still requires its explicit settings and forces automatic reminder activation off. No env_file loader, backend setting or credential copy was added.
- Retired software/.env.production.example after dependency checks and byte-identical ignored recovery at .tmp/task072/retired/.env.production.example: 407 bytes, SHA-256 d056c5a1b669a5b628facba9d0137d92b355bd4ed60062dab37d0ee2b9aed78e. The original was untracked, so no Git-recovery claim. Restore by copying that exact file if needed; preserve old Task 070/071 helpers/results rather than rewriting their hash assumptions.
- Active README links now use the shared template; no app or Compose reference depended on the retired example. Four component/template files pass whitespace checks and 23 component-document relative links resolve. Final combined checks follow after verification.
- Task 072's implementation/config slice is 64 changed lines: gateway +20, edge example +15, Docker pin +1/-1, shared template +9/-2, retired example -16. Tests/docs are excluded; the approved 100-line target is met. Task 070's pre-existing configuration work is not counted as new Task 072 work.

## Isolated verification

- Both Compose modes validate with synthetic settings. Removing each of 11 required production values fails. Custom development ports and the synthetic saved local cutoff remain intact; production activation remains forced empty. No actual installation settings were loaded for these checks.
- Both production targets build. The new Nginx 1.30.6-alpine3.24 serving base was pulled; existing npm-ci/pip dependency layers were reused. Frontend TypeScript/Vite build actually executed, transforming 931 modules with the existing chunk-size warning. No fresh dependency resolution, full unit suite or broad vulnerability scan is claimed.
- Read-only preflight found no host listener or existing Docker binding on 443. The isolated edge binds only 127.0.0.1:443, preserving the exact configured HTTPS origin without test-policy rewrites. Profile-only DNS/certificate pinning and request allowlisting remain required; no system DNS/trust or VPS change. All four source containers remain exited as found.
- Both owned Nginx processes report 1.30.6 and pass nginx -t. Sixteen benign policy cases (four write verbs times foreign Origin, null Origin, same-site and cross-site metadata) return expected 403; 200/401/403/404 responses carry the frame headers. Canonical-origin requests reach ordinary auth, foreign GET still requires auth, and headerless OTP/cookie login/logout works. No prior attack/framing probe was retried.
- Real browser passed four groups: ordinary UI OTP signup/login; name-only meter plus actual readings/top-up and hand-checked forecast; balance/top-up edit/delete/recreate and authenticated deep-link reload; actual UI Sign out followed by /api/me/dashboard 401, then reload remaining signed out. The synthetic example gives 4 kWh/day, approximately 76 kWh/19 days and 44 extra kWh for a 30-day month. Corrections yield 5 kWh/day and return to 4 as expected.
- Five successful desktop/390px captures have no horizontal overflow/nested buttons; forecast captures received visual review. Successful run has zero runtime errors or outside-origin requests and all 68 response peers are loopback. No mocks/session injection or physical-device/household claims. First prelogin harness attempt failed closed with zero app traffic; the ordinary run with approved browser/CDP execution permissions then passed. No root cause or application fix is inferred from that retry; failed evidence is retained, not hidden.
- Both OTP budgets pass using 22 total malformed requests, without retries or actual issuance: one real client hits its 429 limit; three distinct private client IPs (at most five requests each) produce eight aggregate-zone rejections. Zone-specific log evidence confirms both limits, not just a generic status. Before/after counts stay two challenges/two captured emails/zero reminder deliveries: no mail/challenge delta from rate checks.
- Final read-only synthetic DB check finds one UI and one API user, both with zero active sessions after their normal logout flows. No reminder delivery rows. Owned browser is closed with zero Task 072 Node/Edge processes; two ignored profiles remain preserved.

## Cleanup and handoff

- Exact-owned cleanup passes: nine containers (including three bounded-budget drivers), five networks, one synthetic PostgreSQL volume and two task image tags removed. No matching owned containers/networks/volumes remain. Only disposable synthetic data was removed; its test drivers/reports remain locally reproducible. Base images/cache, retired-example recovery, profiles and all old/new evidence are retained.
- Source container IDs/statuses/images/start times/restarts/volumes and actual .env digest match preflight; all four remain stopped as found. Approved runtime-input hashes and the consolidated template hash match the tested versions. No live SQL, source login/mail/restart, real SMTP, reminder activation, backup, sibling edit, VPS/DNS/certificate mutation, commit or push.
- Evidence stays ignored under .tmp/task072/: build logs, resources.json, nginx-checks.json, policy-headers.json, budget-checks.json, browser-results.json/captures, final-checks.json and cleanup.json. No keys/OTPs/cookies/profiles or private settings enter Git/docs.
- Local minimum-pilot configuration and ordinary desktop/mobile flow pass. Next is review and separately approved live Ticket 57.2: inspect the actual shared edge's version/config, set the VPS installation's one .env, and verify real HTTPS/SMTP/app behavior. Local self-signed/captured-mail tests do not certify the VPS, all dependencies or physical/household accuracy. Broad tooling/image scans remain outside this task, not silently reported as passed.
- Production monthly automation remains off pending separate external-mail activation; preserve the existing local cutoff without copying it to the VPS. UI/model/schema/auth contracts and application dependencies are unchanged. Historical Task 071 probe limits/results are preserved; its stopped exploit/framing probe was not retried.
- Final git diff --check, explicit whitespace checks and all 42 relative links across seven active/task documents pass. Retired example is absent and its verified archive exists; actual .env, synthetic key/evidence/archive remain Git-ignored. Only the expected combined Task 070/071/072 public paths are pending; HEAD remains 0d029aef62825be810a8ff7674bffd93e97a2025. Independent runtime/env/evidence review found no local blocker; live acceptance is not claimed.

## Authorized Git handoff

- On 21 October 2026 the user requested committing and pushing the completed work to master. This supersedes the earlier no-Git implementation boundary for Tasks 070-072 only; no new task, runtime change or VPS action is included.
- Independent read-only publication review confirms all 18 pending public paths belong to those tasks. Actual environments, keys, dumps, synthetic reports/profiles and recovery archives remain excluded. No application checks were rerun merely to publish the already-verified files.
- Publish only the explicit reviewed allowlist, without force-pushing or overwriting remote changes; verify the resulting remote master and clean worktree. Any publication failure must be reported rather than recorded as a successful push.
