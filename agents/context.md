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

## Research collection and sending

Research is isolated in software/research/market-research/. Exactly two Python
sources remain: pipeline.py collects/imports; send_due_messages.py sends/reports
and serves the SMS mock. React/FastAPI application code/dependencies are separate.

Canonical private data/contacts.csv: 1,560 unique methods, 643 emails/917 phones,
30 columns and stable remaining IDs. Task 107 fixed three leading email slashes
and merged 582 complete-line phone associations into existing emails, retaining
numbers/context in notes and full recovery/audit in data/task107/apply/. No guessed
excerpt fragments or academic .ac.za emails were added. Preserve IDs, source,
manual/contact/reply/suppression fields and all delivery history.

Task 108 approved/implemented: normal sender invocation reads only this folder's
.env and sends then exits. CONTACTS_CSV defaults to an unsent fictional 10-email/
10-phone fixture at data/local-test/task108/contacts.csv. Loopback SMTP always
requires fictional data and refuses canonical history. Owner switches the same
command to real email by changing research .env SMTP/account values and
CONTACTS_CSV=data/contacts.csv. Never read app .env or inherit SMTP credentials.

Hard cap five attempted contacts/channel/local day across reruns, including
failures/reservations. No weekday/hour gate. Saved UTC timestamps use their
Africa/Johannesburg date for eligibility; future dates wait, blank dates hold.
No date allocation/daemon. Canonical dates/history are unchanged: 30 email slots
across 23-27 and 30 Nov 2026; 613 blank dates. All real attempts/sent remain zero.

Opaque contact groups are manually confirmed only. Any group email takes priority;
real phone rows are unconfirmed/unscheduled. No inferred identities or automatic
follow-up/fallback. SMS remains offline/loopback mock only; real SMTP mode sends
email only. A gateway/API must be chosen before a live SMS adapter can be built.
Do not install/configure Android software or invent a provider schema.

Configured remote SMTP requires credentials and verified STARTTLS/implicit TLS;
no plaintext downgrade or debug/secret-bearing logs. Persist sending before
submission and outcomes immediately under the shared CSV lock. Unknown acceptance
stays held; known acceptance survives failed QUIT. File PermissionError retries
are bounded to three with input rechecks; never retry delivery on unknown result.
Templates stay editable in templates/email.txt and sms.txt; no LLM wording.

Mocks: separate monitor-research-mocks Compose project, loopback 8026 web/1026 SMTP
and 8086 SMS. Captures persist under ignored data/local-test/compose/. No relay or
real credentials in images/mounts. Docker 29 suppresses internal-only port mapping;
its separate bridge does not block outbound traffic. Do not alter app Compose,
working proxies, services, volumes or app .env for this research work.

Collection remains bounded/resumable HTML/plain-text/PDF and local import, with
public-network/TLS/robots/terms/delay restrictions. Eleven failed-source deferrals
and 479 queued URLs remain; no new batch is authorized. Seven manual PDFs/111 pages
were imported and removed only after verified saving; preserve retained evidence,
local_imports.json and unique sources. Optional loopback LM Studio uses grounded
context only; real inference remains unverified. No model/server changes authorized.
Research-only pinned dependencies/venv stay here; all inputs, CSVs, evidence, logs,
credentials, capture tools, generated reports and recovery snapshots stay ignored.

Task 108 verification: 60 checks; actual normal-command Mailpit/SMS capture 5+5, repeated
process 0, next local day remainder 2+2; TLS/auth paths use controlled doubles,
not real provider authentication. Failure/cap/held acceptance and file-retry checks
pass. Canonical CSV, app configuration and templates are hash-protected; own mock
fixture remains unsent. Provider permission/DKIM/DMARC remain unverified; no real
mail/SMS was submitted. Source/status details are in the work records and README.
The owner's final instruction normalized 30 pending email statuses to new:
all 1,560 real methods are unsent with zero attempts, dates preserved. Current
canonical hash/recovery is recorded in data/task108/unsent-reset.json.
Task 105/106 are on master f6c6917/9065e32. The owner authorized committing and
pushing Tasks 107/108; live execution is the owner's later configuration step.
