# Task 071: Browser and Security Readiness

Status: findings-only run concluded on 21 October 2026. Core functional checks pass; browser security coverage is incomplete. NOT READY for a security-cleared merge/deployment. No production fixes or Git/VPS actions authorized or performed.

## Context and reuse

- Read current instructions/context/rules/template, production and relevant component READMEs, Task 070's results, current Docker/proxy configuration, auth/session/OTP/SQL/frontend boundaries and existing browser helpers.
- User confirmed isolated production testing with synthetic regular/admin/shared users and captured email; no source/VPS changes or automatic fixes. This is local evidence supporting Tickets 65/57, not a new roadmap ticket or completion of live 57.2.
- Task 070's production image/API/HTTPS/persistence checks passed and its resources were cleaned. Its probe was not a real browser journey or broad security clearance. Preserve its uncommitted work and existing data.
- Reuse .tmp/task070 helpers and .tmp/task066/run.mjs's Edge CDP driver only. The old browser checks mock fetch: do not reuse that mocking as proof of real end-to-end behavior.

## Preliminary read-only review

- Frontend/Dockerfile pins Nginx 1.30.5. On 21 October the [vendor advisory](https://nginx.org/en/security_advisories.html) lists it within CVE-2026-93479's affected range, with 1.30.6 fixed. The [14 October release notice](https://nginx.org/news.html) records the patch release. This is version evidence, not proof Monitor's exact configuration is exploitable; public-launch recommendation remains withheld pending resolution/retest.
- OTP delivery limits are per normalized email; Monitor's proxy examples contain no aggregate/per-source OTP throttling. Different recipient emails bypass the per-email budget, creating public SMTP/DB abuse exposure. Actual inherited VPS controls are unknown; no load or external-email probe ran.
- Cookie SameSite/CORS do not by themselves establish same-site sibling-origin write protection. Missing explicit Origin/CSRF checks and framing headers are candidates for bounded isolated browser reproduction, not confirmed arbitrary ledger compromise.
- Inspected paths use parameterized scoped SQL, DB-derived roles, crypto OTP/session values and locks. No direct authentication/member/IDOR/SQL bypass or unsafe frontend HTML/storage pattern was found in this limited static review; this is not an exhaustive security claim.

## Preparation checks (before execution approval)

- Independent read-only scope review found no clarification gap; the prompt explicitly requires normal UI OTP login, owned-DB admin promotion, browser-only Monitor/sibling routing, pinned local test certificates/request allowlisting, hash-only source-env inspection and actual fixture state checks for CSRF.
- No new containers, browser, runtime tests, dependency scanner, production-code fix or source/VPS action has run for Task 071. Only public advisory lookup and local read-only inspection preceded prompt preparation.
- git diff --check, explicit whitespace and all 31 relative links across the five Task 071 preparation documents pass. Changes in this preparation are documentation only; pre-existing Task 070 runtime/config work is preserved.
- Runtime/config edits already present belong to completed Task 070. No commits, merges or pushes are authorized by this task.

## Approved execution boundary

- The user requested executing the completed Task 071 prompt. Reuse exact current production candidate files, without patching the known Nginx pin or changing authorization/UI/configuration to make tests pass.
- Build/run only separately labelled synthetic resources. Source service inspection is metadata/hash-only; source .env contents are never loaded as test configuration. Browser traffic is restricted to owned loopback endpoints with profile-local hostname mappings and local certificate pins. No source SQL, real email, live DNS/proxy/certificate operation or source service change.
- Test admin promotion and expired/revoked fixtures apply only to the new synthetic database. Normal UI OTP flow must establish browser sessions; mocks/session injection do not count as end-to-end evidence.
- Security findings, scanner gaps and test limitations will be reported even if functional journeys pass. No claim of vulnerability-free software or final live acceptance.

## Execution evidence

- Source preflight found all four development containers already exited (255), unlike Task 070's running completion state. Read-only independent inspection confirmed this. The guard was adapted to preserve the actual stopped identities/statuses/volumes, not start or repair the source stack. Source .env is checked by digest only.
- Both exact current production Dockerfile targets built/exported successfully using matching cached dependency AND app/build layers. No fresh pip/npm resolution or TypeScript compilation is claimed for Task 071; prior Task 070/069 build results remain historical evidence.
- Fresh labelled synthetic PostgreSQL had zero users/meters/deliveries. Production automation remains hard-off. Docker Desktop did not allocate a loopback-published port while the mock edge joined internal networks only; the test setup stopped before browser traffic, then added one task-only edge ingress bridge with masquerading disabled. All app/database/mail/probe networks stay internal; only the edge publishes random 127.0.0.1 TLS. No production configuration changed.
- Bounded real API checks pass: 17 unrelated-user nested reads/writes denied, membership revocation denied, invalid/expired/revoked sessions and invalid/expired/replayed OTPs rejected, five-attempt exhaustion/resend cooldown enforced, SQL-like names/search kept literal and invalid kWh rejected. Three distinct recipient challenges actually persisted from one client; no flooding or real mail was used. Automatic delivery rows remain zero.
- Browser attempt one stopped at target attachment before navigation/login and closed its owned browser. The driver now explicitly attaches each blank target and installs fail-closed policies before navigation; child-target protection remains. Attempt two passed real UI login, both rename paths, record corrections and valid/unavailable forecasts but stopped at a harness Delete selector after History collapsed; no DELETE request occurred. Only the test driver was adjusted to reopen the details/tab; candidate app code stayed unchanged.
- Desktop/390px synthetic forecast screenshots were visually inspected: readable without horizontal overflow; approximately 76 kWh / 19 days / 44 kWh extra correctly follows 4 kWh/day, a 30-day planning month and current balance. This is viewport emulation, not physical-phone or household validation. Final results and coverage limits follow below.

## Dependency/advisory evidence

- Read-only public npm lockfile audit reports two high-severity package identities: Vite 8.3.1 and source-map-js 1.2.1 through PostCSS. These are development/build tooling, not Node services in the final static Nginx image. No audit fix/install ran; exact details are in ignored .tmp/task071/advisory-npm-audit.json.
- OSV checked all 26 installed backend Python package versions. Matches cover pydantic-settings 2.13.1's unused nested-secret feature, pytest 9.0.2's local temp-directory issue and pip 26.0.1 installer/supply-chain issues; six distinct issues after alias deduplication. These are conditional/local/build findings, not demonstrated remotely reachable Monitor endpoint compromises. Raw direct/full inventory queries and primary maintainer links are retained in ignored .tmp/task071/advisory-summary.md and related JSON.
- Nginx's affected-version finding remains unresolved because fixes are out of scope. Runtime inventories identify Python 3.14.4, Nginx 1.30.5, PostgreSQL 17.11, Debian-family backend packages and Alpine 3.24.2 frontend/database packages. A full OS/native-library/SBOM vulnerability scanner was unavailable; inventories and selective vendor checks are not a clean-image certification.

## Final browser results and limits

- Real Edge CDP used a fresh task-only profile, local hostname mapping/certificate pin and owned-origin request allowlist. No API mocks, browser session injection, system DNS/trust changes or public VPS requests. Recorded response peers are loopback; saved run has no blocked requests or runtime errors.
- Four functional groups passed: normal UI OTP signup/login; both meter rename paths and balance/top-up create/edit/delete; sharing/member writes, unrelated access denial, revocation and last-member guard; normal signup followed by isolated DB admin promotion and correct My/All/global detail access. Deep-link reload retained saved records and the hand-calculated forecast. Correction examples changed the derived rate from 4 to 5 kWh/day and back, as expected.
- Nine successful captures cover login, empty state, forecasts, record form, sharing and admin views at 1200/390/320px as applicable. Layout checks show no horizontal overflow or nested buttons. Desktop/390px forecast and 320px/admin captures received visual review. No physical-device or household validation is claimed.
- Test-only input readiness and navigation guards were strengthened after harness races; navigation now requires the requested origin/path. No candidate application code or assertions were weakened.
- The bounded sibling-origin check stopped at an evidence assertion: the captured CDP request event omitted Origin (null). There was no completed response/status; read-only preservation found ZERO balance rows in the separate disposable security meter. Therefore CSRF was NOT demonstrated, and successful protection was NOT established. A subsequent execution safeguard prevented continuing that security work; no retry or workaround was performed.
- Framing and ordinary UI sign-out checks were not reached. API logout/revocation passed independently; that is not a completed UI sign-out journey. The full browser result is marked failed/incomplete, not an all-green run.

## Findings and proposed follow-up (not implemented)

| Finding | Evidence / severity | Smallest follow-up |
| --- | --- | --- |
| Affected production Nginx version | frontend/Dockerfile:18 pins 1.30.5; CVE-2026-93479 vendor severity medium, fixed in stable 1.30.6. Gateway variable proxy_pass is relevant, but exact exploitability was not demonstrated. | Separately approve a supported patched image pin, rebuild and repeat gateway/functional acceptance. Do not assume the real shared edge version. |
| OTP abuse across different emails | endpoints/auth.py:47 and modules/otp.py:14-16,89-105 enforce per-email limits only; neither Monitor Nginx config adds aggregate/client limits. Three distinct challenges persisted from one client. Assessed medium availability/mail-cost exposure, not authentication bypass or a load test. | Add small public-edge per-client and aggregate request-OTP budgets before client addresses are stripped; preserve the existing per-email/attempt rules. Verify behavior without flooding. |
| Origin/framing protection unverified | main.py:25-28 configures CORS; auth.py:150-158 sets Secure/HttpOnly/SameSite=Lax. No explicit unsafe-request Origin/CSRF check or frame policy was found in Monitor's configs. Severity unassigned: browser reproduction is incomplete. | Review a minimal unsafe-request origin/CSRF boundary and anti-framing policy, then complete authorized acceptance. Do not interpret CORS or SameSite alone as proof. |
| Dependency/tooling maintenance | npm: two high package entries, both dev/build paths. Python: three package identities/six issues with conditional, local or installer preconditions. Full OS/native scan unavailable. | Separate narrowly scoped updates/image review; do not present these as demonstrated public endpoint exploits or silently run audit-fix. |

These paths are relative to software/backend/app/ or software/frontend/ as named;
the two proxy configs are software/frontend/nginx.conf and
software/production/monitor-edge.conf.example. Public advisory metadata, version
inventory and reachability notes remain in the ignored advisory report.

## Readiness decision

- Merge recommendation: hold the production candidate's deploy-ready handoff until the affected Nginx pin and OTP aggregate-abuse findings are resolved/reviewed. The evidence report itself is reviewable; no Git operation was performed. Findings-only scope does not authorize fixes.
- Deployment gates: settle origin/framing protection and close the incomplete browser acceptance, then perform separately approved real VPS edge/TLS/provider/deployment-isolation acceptance. Full OS/native coverage is still a limitation, not a clean-image claim. Local functional evidence supports Tickets 65/57 but closes neither household usability nor live 57.2.
- Residual risks: bounded tests are not exhaustive; per-email limits do not establish fleet-wide abuse protection, synthetic viewport tests are not physical/household evidence, and local self-signed/captured-mail success cannot guarantee vulnerability-free software.
- Keep existing deterministic per-meter calculations. No forecasting, schema, auth contract, UI, dependency, application runtime/configuration or reminder activation change was made by Task 071. Pre-existing Task 070 changes are preserved, not published.

## Preservation, cleanup and evidence

- Guarded cleanup passed: removed only six owned containers, five owned networks (including the edge-only no-masquerade ingress), one synthetic PostgreSQL volume and two task image tags. Their synthetic data is intentionally removed; reports/screenshots remain ignored locally. Base images/cache and all source volumes/data/backups/research remain untouched.
- Zero Task 071 profile browser processes remain. Four ignored test profiles are retained, not recursively deleted. Source container IDs/images/start times/restarts/volumes and actual stopped status, source .env digest and all frozen runtime/config inputs match preflight. All four source containers were already exited 255 and remain stopped; no restart, SQL, real email or source login was performed.
- Retained ignored evidence: .tmp/task071/api-security.json, browser-results.json (four passed groups plus incomplete run), preserved-browser-observations.json, browser-process-proof.json, cleanup.json, advisory-summary.md, raw npm/OSV results, image inventories/build logs and synthetic browser-*.png. None of these profiles, synthetic secrets/certificates, OTPs or cookies are committed or pasted into public docs.
- No backup, sibling edit, external SMTP, VPS/DNS/certificate mutation, commit, merge or push.
- Final git diff --check, explicit whitespace checks and all 32 relative links across the five Task 071 documents pass. No full application unit suite or fresh TypeScript compilation was run in this findings-only task; actual verification is the cached-target builds, isolated real API/browser work and advisory review described above.
