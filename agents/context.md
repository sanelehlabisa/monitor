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

One ignored `software/.env`, one safe example, exactly dev/prod Compose files.
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

`software/research/market-research/` is isolated from the app. Task 103 implements
one typed pipeline.py: bounded resumable HTML/plain-text/PDF collection, public
email/phone extraction, ZA-aware normalization and independent pair deduplication.
Research-only pypdf 7.1.1 and phonenumbers 9.0.44 stay in its local .venv.
New originals are not saved; old captures, seeds and failed-list history remain.

One canonical private data/contacts.csv has the approved 15 columns and stable
IDs. Preserve manual/status/contacted/response fields; fill blanks and keep
conflicting named facts in notes. Atomic writes, external-edit checks and one
shared contacts.lock protect it across checkpoint directories. Save contacts
before a page is complete; reuse extracted evidence without refetching. Old text
cannot reveal previously unrecorded tel hrefs. Unknown identity fields stay blank;
free-mail domains or page publishers never establish the contact's organisation.

Optional loopback LM Studio gets only bounded contact context; validate five
string fields against nearby prose, cache successes and fall back on outage,
invalid output or budget limits. No tools, cloud models or downloads. Small Qwen
is preferred only when advertised by the local API; its actual installed ID is
unconfirmed because the server was unavailable. Real inference remains unverified.

Honor robots, TLS/public-IP checks, delays, depth, per-seed/domain/request limits
and all 11 links.failed.txt deferrals. Log actual restrictions in private
data/blocked_urls.csv; rate deferrals and transport/redirect errors are distinct.
Task 103: 58 direct checks; one live run used 20 requests and produced 109 unique
contacts (50 emails, 59 phones), one known blocked source and zero new errors.
479 URLs remain queued at scope/domain limits. Real inputs/results stay ignored.
No app changes, sending, SMTP checks, outreach drafts, service restart or Git
publication. Task 103's approved local extension adds --import-dir and explicit
--delete-imported, reusing the same readers/CSV with no web requests. Unique
seed/failed filename matches retain their URL; unmatched sources use a validated
local URI and blank domain. Save and verify extracted evidence/contacts, then
recheck the exact input path/content before individual removal. Keep failed,
partial, encrypted, textless, challenge and changed inputs. Never remove folders.

Local extension: 33 focused checks and the approved seven-PDF import passed.
All 111 pages extracted completely; 2,087 contacts added, zero errors, all seven
inputs verified/removed. The import produced 2,196 unique rows before the owner's academic-email cleanup.
Prior 109 IDs/fields and 36 protected files remain unchanged. No web/model calls.
Exact source paths/hashes/cleanup proof are private in data/local_imports.json;
extracted JSON remains, with no replacement raw archive. The empty links.failed/
folder stays. Web state, failed URL list and blocked audit are unchanged. Next:
owner CSV review; later research/outreach still needs its own approval.

Task 103 is complete within its approved scope. Current CSV has 2,142 unique rows (643 emails, 1,499 phones) after the owner
requested removal of 54 .ac.za email rows. All retained rows/IDs and phone records
are unchanged. Private removal audit: data/task103-academic-email-removal.json.
No ingestion-code filter was added; future collection must honor this preference.
No local inputs remain, and the successful cleanup audit is preserved. The
configured local LM API at 127.0.0.1:1234 still refuses connections when checked
outside the sandbox; optional real inference remains unverified. No new crawl
batch, model/server operation or outreach is authorized by this completed task.
