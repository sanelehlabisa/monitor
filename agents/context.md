# Monitor context

## Current system

Prepaid-electricity planner. Source now has a local-only `/guest` workspace for one
meter, with the existing forecast/ledger UI. Task 092 is not deployed; the owner
reports the earlier email-login deployment working. Account access uses email OTP.
Users record balance/top-up kWh and occurrence times.
Named meters can be shared; members and DB `users.type=admin` have full access
within their scope. Open signup creates regular users; roles never come from
email/environment. Fresh seeds create the approved admin in both modes and
fictional meters only in development. Existing volumes never replay seeds.

React/Vite/Material UI; FastAPI, Psycopg and PostgreSQL with pure SQL.
Backend: `software/backend/app/{endpoints,modules,schemas}`.
Frontend: `software/frontend/src/{routes,components,lib}`.
Store UTC; input/display uses local time. One actual balance uses a labelled
10 kWh/day starting rate; valid intervals supply per-meter measured use.
No balance/inconsistent history stays unavailable. Show current balance,
remaining days/run-out, additional top-up and total monthly requirement.
Plan for strictly-next UTC 1st using the actual target month's length.

Opaque cookie sessions store only digests; current new-session lifetime is
30 days. Preserve OTP limits, server expiry/logout revocation, origin checks
and live role/member authorization. Monthly email has durable recipient state;
only monthly planning is automated. Production activation remains explicit.

## Next work

68.1–68.3 implemented: `routes/guest/{GuestPage,localMeter,forecast}`,
versioned `monitor.guest.v1` browser data and integer-unit forecast parity. Guest
records never enter API requests. Blocked/full storage keeps in-memory records;
corrupt data and detected tab conflicts are preserved until explicit recovery.
Account sessions never enter the guest store. Browser saving is not permanent.
Entry: home introduces balance, run-out and monthly purchase estimates with a
light-blue introduction, teal icons and one Log in action; `/login` offers
email or guest with an “or” divider. The app uses Monitor branding. Guest pages
omit routine storage/login-to-save copy; genuine failure warnings remain.
Next 68.4: the chosen account-saving flow, saving existing local history
after successful OTP without a separate copy screen. Retain originals, handle
retry/partial saves and hide the prompt after login. Ordinary login does not import.
68.6: unchecked-by-default Keep me signed in; checked lifetime is confirmed 3 days.
Existing runtime still uses 30-day sessions until this planned change is implemented.
Then 65 usability, 57.3 deploy and 67 recruitment/approximately 30-day feedback.
Native/PWA 68.5, research 66, hardware/OCR/ML, tariffs and payments stay later.

## Operations

The Monitor app uses one ignored `software/.env`, one safe example and exactly
dev/prod Compose files. Research has its own independent .env, described below.
Development uses localhost/Mailpit overrides. Production serves internal HTTP80
as `monitor-frontend` on external `roventics_proxy`; public HTTPS is upstream.
Backend/database are private; no production Mailpit. See `software/nginx/README.md`.
Preserve working routing, live data, backups, `refocus.md` and unique research.
Task 092 verified: build, 44 existing checks, 215 Python/browser forecast cases and
9 isolated browser groups. No source services, live data or deployment changed.
Entry refinements are recorded in Tasks 093–095. Task 095's build, 44 existing
checks and 1280/390/320px walkthrough pass. Root README owns priorities;
component READMEs own detail. Task 096 removes the company footer and prepares
the beta handoff. The user approved Git publication on 3 November 2026;
VPS rollout is the next operator step.
Task 097 restores the original company logo credit and improves homepage canonical
and nonpublic noindex headers, without changing account flows or landing copy.

## Research collection

Task 103 collection is complete, preserved in master commit e4a7ff1.
`software/research/market-research/pipeline.py` is isolated from the app. It
supports bounded resumable HTML/plain-text/PDF crawling and local saved-file
import, public email/phone methods, ZA-aware normalization and independent pair
upserts. pypdf 7.1.1/phonenumbers 9.0.44 stay in the research .venv.

One canonical private data/contacts.csv now uses 30 columns and stable IDs;
the original 15 research fields are preserved. Preserve manual/status/contacted/response fields. Current review output:
2,142 unique contacts (643 emails, 1,499 phones). The owner removed 54 .ac.za email
rows directly; no ingestion filter was added, so future collection must honor
that preference. Keep university-hosted private-provider phones; do not infer
ownership from publishing sites. All real inputs/results remain ignored.

The seven manual PDFs (111 pages) were fully imported; originals were removed
only after verified evidence/CSV saving and input rechecks. The links.failed/
folder is empty. Exact paths/hashes/proof are in data/local_imports.json; extracted
JSON remains without raw replacements. --import-dir and explicit --delete-imported
reuse the same CSV; retain failed/partial/textless/changed inputs. Do not remove
folders, follow embedded links or relax public-network rules for local import.

Honor robots, TLS/public-IP checks, delays and seed/domain/request limits. All
11 links.failed.txt deferrals and 479 queued URLs remain; no additional web batch
is authorized. Optional loopback LM Studio validates grounded strings and caches
successes; unknown identity fields stay blank and domains/publishers never imply
an organisation. The configured 127.0.0.1:1234 API refused connections at the last
check; real inference is unverified. No model/server change is authorized.
Verification/results: 58 collection and 33 local-import checks; see Task 103.

Task 105 and its owner-requested simplification are complete; real delivery remains disabled.
Exactly two Python source files under software/research/market-research/: pipeline.py
(collect/import) and send_due_messages.py (CSV due-date checks, local transports,
reports and optional read-only setup inspection). No separate scheduler/helpers.
The collector preserves delivery fields on upsert. Runtime never allocates dates.

Real CSV: 2,142 rows unchanged in original fields/IDs; 30 email reservations,
613 email rows unscheduled, all 1,499 phone rows held. No actual attempted/sent/
contacted updates. Six dates: 23-27 and 30 Nov 2026; five/day at 09:30, 11:00,
12:30, 14:00, 15:30 Johannesburg (closing minute included), stored aware UTC.
Target five/channel/day; hard cap six attempted contacts/channel/day, one automatic
attempt per row/channel/day and at most three safe attempts. CSV timestamps
control eligibility, including overdue dates after the initial November batch.
No hardcoded date expiration; weekdays/hours/caps remain. No recurring job installed.

contact_group is manually confirmed only; no person inference from sources.
SMS needs a confirmed complete phone-only group and mobile-capable number type.
Any group email has priority even if failed/not due; sent/contacted/replied groups
block further initial contact. No automatic channel fallback or follow-up. Preserve
all phone rows and fixed exact templates. The SMS boundary is offline-only; future
gateway env keys cannot enable HTTP. No Android software was installed/configured.

A shared contacts lock plus guarded atomic writes save sending/attempt state
before submission. Unknown acceptance stays sending for manual review, never
automatic retry. Known SMTP acceptance stays sent even if QUIT fails. Persistence
failure stops further attempts. Test mode refuses real CSV/aliases and non-fictional
provenance, uses loopback SMTP and never loads production credentials. No real
email or SMS transport/production flag exists. Bare runner invocation safely
shows due candidates; --report on the real CSV is read-only.

51 direct checks and actual native Mailpit/offline SMS capture passed: five
fictional emails + five SMS mocks, one controlled failure/channel, fresh-process
restart zero resends, weekend zero submissions. Docker was unavailable; official
pinned Mailpit 1.31.4 was checksum-verified in ignored local-test/, then its owned
capture process was stopped. No app services changed. Private evidence/reports:
data/task105-verification.json, local-test/demo/, schedule-proposal.json and
email-readiness.json. Before-state audit and all source evidence remain private.

Research sender is sanele.hlabisa@roventics.com. Latest owner instruction requires
independent software/research/market-research/.env; the runner never reads/falls
back to app/process SMTP settings. App software/.env is byte-for-byte unchanged.
The research file has starting server/port/TLS only; own SMTP username/password
and future SMS credentials are blank for the owner to fill. No app secrets copied.
Research .env is ignored; its own .env.example is reviewed safe source. Only the
research additions were removed from the app example. An old unused research key
in the actual app .env is deliberately untouched under the owner's instruction.
Readiness reports missing own credentials and no-auth TLS/public DNS; previous
TLS/SPF passed, DMARC absent, DKIM/sender permission unverified. No AUTH or real
message. Mocks do not need real credentials; production still needs explicit
approval and gateway selection. python-dotenv/dnspython remain research-only. Task 104/survey stays deferred. No
scraping, inbox polling, real sending, Android setup, commit or push in 105.

The simplification retained all CSV bytes/reservations and exact messages; 27
regression checks cover date/time/caps, restart, priority and guarded local tests.
Retired outreach.py, schedule_messages.py and email_readiness.py after checking
imports and a verified private source recovery ZIP. Recovery/audit/checks are
under data/task105-simplification-*. No new messages, install, commit or push.

For eligible new/scheduled rows, setting/clearing the channel scheduled_at cell
queues/holds the contact without a separate status edit. Sent/failed/held states,
per-day caps and manual-review rules still apply. No CSV bytes were changed by
this correction.

Task 105 template/readiness correction: fixed wording now lives in reviewed
UTF-8 templates/email.txt (Subject line + body) and templates/sms.txt. Runner
loads once per delivery invocation; no message literals or interpolation in
Python. Sent/held states never reset after edits. Still two Python files.
13 focused checks plus new actual Mailpit/offline SMS capture pass (five/five,
restart zero); the owned capture process was stopped. A fresh unsent fictional
five-email/five-SMS fixture is ready at data/local-test/ready/contacts.csv.
Start local Mailpit first; the README gives both commands and a weekday --now
simulation. No Android gateway needed for mocks. Real CSV is unchanged and real
delivery remains disabled. Private results: data/task105-template-*.json.

Research-config isolation: nine focused checks verify the exact config path,
no app/environment fallback, secret-free reports, missing-config handling and
unchanged app .env/contact CSV. Research SMTP/SMS values may now change
independently. No new script, app/service operation or real delivery.
