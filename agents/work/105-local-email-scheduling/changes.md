# Task 105 preparation

The owner refocused the research workflow to one exact research email, CSV-based
scheduling/tracking and local capture before any production sending. They
confirmed sanele.hlabisa@roventics.com as the research sender. Task 104's missing
survey is no longer a dependency; preserve it as deferred work for later replies.

Inspected current instructions, the CSV contract/writer/lock helpers, existing
app mail configuration pattern and research dependencies. Read only config
presence and nonsecret sender/port/TLS details; no passwords or credentials were
printed. Current app sender is info@roventics.com, with SMTP port 587 and the
implicit-TLS flag false. Sender permission and outbound DNS are not yet verified.
Asked about the sender, optional DKIM selector and missed-day handling; recorded
the supplied sender. Docker CLI exists, but the local engine did not respond.

Read-only contact counts: 643 emails and 1,499 phones, all legacy new/uncontacted,
no responses and no .ac.za email rows. Calendar verification confirms six
weekdays from 23-30 November 2026, allowing 60 slots at ten/day. No contact content
was printed and no CSV/config/service changes were performed.

Prepared prompt.md from agents/prompt.md for owner Tickets 1-4, mapping them to
existing roadmap IDs and small 71.10 sub-tickets. Added a proposed last-attempt
timestamp for actual daily caps across restarts and an in-progress/manual-review
rule for ambiguous delivery. Consulted official Python SMTP, Mailpit and SMTP
protocol references. Templates do not vary; production delivery remains excluded.

Updated concise roadmap/current context and deferred Task 104. Replaced obsolete
per-contact-personalization/survey-first requirements in the active research
README; prior instructions remain in historical work records. No source code,
dependencies, schema migration, real schedule, DNS probe, SMTP submission, model
operation, app change, test capture, commit or push has been performed for 105.
Implementation awaits prompt approval and clarification where still needed.

## SMS refocus preparation

The owner adds local-only SMS abstraction/configuration and shared tracking,
changes both channels to a five/day target with a six/day hard cap, and requires
email-first priority without automatic follow-up. Retained Task 105 rather than
creating a duplicate ticket. Its email sender/template and readiness/local SMTP
scope remain; actual email scheduling code is not yet implemented.

Reinspection confirms 2,142 rows with no delivery columns or person/group IDs and
zero explicit names. Phone-number metadata counts 1,391 mobile, 107 fixed-line
and one VoIP; this is not proof of capability or shared identity. Asked about
manual grouping versus an owner-provided mapping. Revised the prompt to propose
one manual contact_group, per-channel state/attempt timestamps and an unscheduled
hold for unconfirmed phones. Never infer person links from publisher domains or
nearby text. The existing 23-30 Nov window now has 30 target slots/channel, with
SMS allocation awaiting confirmed phone-only contacts.

The planned send_sms boundary is an offline mock only. Future environment key
names do not enable any real gateway. No Android/network SMS code, download,
installation, .env values, CSV migration, schedule, local message, code change,
service operation or production delivery has occurred. Updated active guidance
and roadmap to replace the previous ten-email/day draft and generic email-state
proposal; new per-channel names are planned directly from the actual 15-column
CSV. Implementation still needs approval of the revised prompt.

Preparation checks passed: exact email/SMS bodies, 30 target slots/channel,
26 relative documentation links and whitespace. Source/dependencies and the
2,142-row/15-column CSV are unchanged; its hash matches the prior cleanup.

## Implemented and verified

The owner approved revised Task 105, including the conservative manual grouping/
phone hold. Added outreach.py, schedule_messages.py, send_due_messages.py and
email_readiness.py with explicit modes and few shared helpers; no daemon,
database/queue, application import or production transport. Modified pipeline.py
only for delivery defaults, old/expanded contact headers and preserving new
fields on upsert. Kept the existing CSV/atomic-write/lock/normalization helpers.

The 30-column contract retains all original 15 fields and adds contact_group,
email/phone mirrors and six state fields per channel (including last_attempt_at).
Shared group priority prevents automatic SMS where email exists, sent/contacted/
responded groups cannot receive another initial message, unknown phone links are
held, and fixed-line/uncertain SMS types stay ineligible. No links are inferred
from publisher domains, nearby text or shared files. .ac.za email exclusion is
also enforced at delivery eligibility. Exact templates match the owner's text.

A single-pass local runner counts actual per-channel day reservations/successes,
rechecks local working time before every attempt and saves sending/attempt data
before submission. It updates accepted/rejected outcomes immediately. Six is the
hard daily attempt cap, five the scheduling target, one auto attempt per row/
channel/day and three total safe attempts. Known temporary rejections may retry
on later working days; permanent failures stop. Unknown acceptance/interrupted
sending is a manual-review hold. Failed final SMTP QUIT cannot undo known DATA
acceptance. Failed persistence or writer conflicts stop further submissions.

--local-test requires synthetic example.invalid provenance under data/local-test/
and rejects the canonical CSV, aliases and non-fictional data. SMTP is pinned to
127.0.0.1; no production credentials are loaded. send_sms is an offline mock with
controlled errors and no HTTP/Android code. Gateway URL/key settings cannot enable
any real transport. Future blank key names are documented in software/.env.example.
Only RESEARCH_EMAIL_FROM was appended to the one ignored software/.env; existing
app sender and SMTP keys/values were preserved. No gateway values were set.

### Checks and actual captures

51 direct checks passed with fictional temporary fixtures driven from stdin;
no persistent test files. Covered old-header migration/original field retention,
stable/idempotent schedules, all working-hour/weekend/date fences and UTC offsets,
per-channel caps, previous attempt counts, restart/no resend, email/group priority,
reply/academic/landline/unconfirmed holds, bounded retries, permanent/uncertain
failures, CSV write/external-edit/lock failure, collector state retention, rejected
real-data delivery, offline SMS despite gateway env keys, SMTP MAIL/DATA/QUIT
outcomes, strict readiness TLS and unverified DNS behavior. An identical schedule
audit safely resumes after a simulated save failure without overwriting history.

Docker's engine remained unavailable. For the actual SMTP test, downloaded the
official Mailpit v1.31.4 Windows release into ignored data/local-test/ and verified
its archive SHA-256 against official release metadata. No global installation or
Android tool. Source/hash are in data/task105-mailpit-tool.json. Started only an
owned hidden capture process on loopback 8026/1026, with a fictional-recipient
allowlist, no forwarding/relay config, no version check and reverse DNS disabled.
Cleared inherited MP_* settings for that child process only. Mailpit's internal
capture store is a private test artifact; CSV remains the outreach state source.

Actual fictional-run results:

```text
Emails sent today: 5
SMS sent today: 5
Emails sent this run: 5
SMS sent this run: 5
Email failures: 1
SMS failures: 1
Remaining email contacts: 0
Remaining SMS contacts: 0
```

The deliberate SMTP recipient refusal and SMS-mock permanent failure were saved
while other contacts succeeded. All five MIME messages and SMS bodies match the
fixed wording; compare MIME-decoded text with normal wire-newline normalization.
The initial capture assertion compared CRLF wire text with LF source text; the
corrected comparison verified the existing captures without resetting/re-sending.
A fresh Python-process restart submitted zero messages and left the CSV/capture
count unchanged. A weekend run made zero attempts. The owned Mailpit process was
stopped in finally after each capture inspection. Demo logs/raw captures/CSV and
results remain private under data/local-test/demo/ and data/task105-local-capture.json.
No actual recipient received anything; no real gateway was called.

### Read-only readiness

Used python-dotenv 1.2.4 and dnspython 2.9.2, pinned only in research requirements.
No backend/frontend dependencies changed. The first TLS probe exposed missing
hostname propagation in the new inspector; fixed client construction, preserving
normal hostname/certificate verification. The completed probe used only SMTP
connection/EHLO/STARTTLS and close: no AUTH, MAIL, RCPT or DATA to real SMTP.

Readiness evidence: TLS verified; SPF record published; DMARC absent; DKIM
selector/signing and SMTP sender authorization unverified. Three blockers are
explicit in private data/email-readiness.json. Record presence is not proof of
alignment or real signing. Production remains disabled, and no DNS or provider
configuration was altered. An inspection exit code of zero is not send approval.

### Saved real schedule and preservation

After all local capture checks passed, previewed and explicitly applied the
canonical schedule, then repeated apply with zero additional reservations.
Scheduled 30 emails (five/day on 23-27 and 30 November 2026), at local 09:30,
11:00, 12:30, 14:00 and 15:30; all aware UTC timestamps. Hard cap remains six.
613 emails stay unscheduled. All 1,499 phones remain held pending confirmed
complete phone-only groups; no invented cross-method identity or SMS reservation.

Final canonical CSV has 2,142 unique rows/IDs and 30 columns. Projecting original
15 columns recreates the exact pre-task CSV hash; order/IDs/notes/context and all
legacy contacted/response fields are unchanged. All real per-channel attempt
counts are zero and sent timestamps empty. All 43 protected input/evidence/web
state files passed hash-preservation checks. No crawl or evidence replay occurred.
Private before/migration audits and proposal: data/task105-before.json,
data/schedule-*.json, data/schedule-proposal.json, data/task105-verification.json.

Updated active context and research instructions/roadmap. Source allowlist names
only the four reviewed new Python files; all data/captures/tools/config secrets
stay ignored. No app service/Compose change, real email/SMS, Android setup,
recurring job, survey work, LLM copy, Git commit or push. Next work remains review
of readiness blockers and separately authorized production email / chosen SMS
adapter, not implicit activation.

Final checks passed: syntax for all five research modules, exact templates,
26 relative documentation links, pip check, offline pipeline --check, whitespace,
ignored private outputs and full canonical field/protected-file preservation.
The shared writer lock is released; no owned capture process remains running.

## Owner-requested simplification

The owner directly requested one or two scripts and decisions based on saved
CSV send dates rather than a separate schedule-building invocation. Applied this
correction within approved Task 105, keeping real delivery disabled. Scope and
checks were recorded first in simplify-prompt.md; no new transport/production
permission was inferred.

Exactly two source files remain in the experiment: pipeline.py (unchanged in this
correction) and send_due_messages.py. Moved shared state/local transports and
read-only readiness functions into the runner; optional DNS/.env imports are
lazy. Removed runtime slot generation, schedule assignment and the unrelated
hardcoded 23-30 November eligibility fence. Current CSV dates, including overdue
dates, determine due contacts under current weekday/hours, caps and priority.
Blank/future dates stay unsent. Runtime does not allocate or rewrite send dates.

Bare invocation now reads/checks the canonical CSV and shows current due IDs with
a clear real-delivery-disabled label. --report, --check-setup and --local-test
remain optional modes of the same file. Default due selection and local-test
execution share the same candidate ordering/cap/group logic. All existing
restart/manual-review, sent suppression, SMS mock and contact priority safeguards
remain. No functional real-email/SMS mode was added.

Retired these exact paths only after dependency and recovery verification:

- software/research/market-research/outreach.py
- software/research/market-research/schedule_messages.py
- software/research/market-research/email_readiness.py

They were uncommitted, so preserved exact source bytes plus the previous runner
and allowlist in ignored data/task105-simplification-recovery.zip. Verified every
member and SHA-256 before retirement; paths resolved to regular files directly
inside the experiment. data/task105-simplification-before.json records hashes.
No recursive deletion, research/evidence retirement or user-data deletion.

27 focused direct checks pass: old/same/future/blank CSV dates, eligible dates
beyond the former expiration, year changes, weekdays/hours, actual-time ordering,
default safe invocation, selected local submissions, no restart resends, unchanged
scheduled timestamps, SMS mock/unknown holds, daily cap, email priority/failure,
real-data rejection, merged no-auth TLS behavior and exact retained messages.
Original canonical CSV hash is unchanged, including all 30 saved email slots.
Readiness evidence and previous Mailpit/SMS captures remain intact. No actual
server/gateway use, new install, contact attempt, schema change, commit or push.

Updated active usage/context/source allowlist to the two-file layout. Prior
Task 105 results/file-layout references above remain historical records; recovery
is available privately. The original November schedule remains data, not a runtime
cutoff. Real sending still requires its separate explicit approval.

The date-control correction also accepts an eligible new row with a saved send
timestamp and ignores a blank send date even when its unsent state is scheduled.
Both cases pass focused checks; users do not need a separate status-edit step.
Successful/failed/manual-review and contacted protections remain unchanged.

Final correction checks pass: exactly two source files, syntax, all 27 relative
documentation links, offline collector check, whitespace and ignored recovery/data.
A December 1 read-only run selected six overdue email IDs under the cap; the
completed fictional demo still produced zero resends. Canonical CSV hash matches
the correction baseline; no real messages or saved-date changes occurred.

## Editable templates and owner mock readiness

The owner asks whether both-channel mock testing is ready and requests editable
email wording outside Python. Applied this within the fixed-template/local-only
scope. Moved the exact approved subject/body to reviewed templates/email.txt and
SMS text to templates/sms.txt. Updated the allowlist only for these two source
files. The email file has one Subject: header, blank separator and body. The
runner loads a bounded UTF-8 snapshot once per run and passes it into local
transports; editing it applies next invocation, never resets sent state, never
interpolates recipient variables and never executes content. Malformed, missing,
empty, header-injected or oversized templates fail before marking an attempt.
No extra Python file, dependency, schema or production mode was added.

13 focused checks pass: original text hashes, file edits/reload, invalid formats,
size/header guards, literal braces, generated MIME content, two-script layout,
unchanged real CSV and the unsent fictional owner fixture. Actual capture with
the updated file loader verified five exact-text Mailpit emails and five offline
SMS messages. A fresh process sent zero again, and a simulated template edit did
not reselect sent rows. The owned capture service was stopped in finally. Its
private artifacts are under data/local-test/template-check/ and the evidence is
data/task105-template-checks.json / data/task105-template-capture.json.

Prepared separate data/local-test/ready/contacts.csv for the owner, with five
fictional email rows and five confirmed fictional phone-only groups, untouched
attempt counters and saved past dates. Did not consume/reset this fixture during
verification. The README provides the existing Mailpit start command, the one
local-test runner command with a Tuesday working-hour simulation, capture paths
and expected first-run/restart behavior. This avoids the previous confusion of
rerunning an already completed demo. SMTP capture must be running before its
first email test; offline SMS needs no gateway. Production DNS/sender blockers
are unchanged and do not prevent local tests. No real email/SMS, Android setup,
actual contact changes, commit or push.

## Independent research SMTP/SMS configuration

The owner explicitly requires a private .env inside market-research, independent
of the app, and forbids editing the existing actual .env. Created ignored
software/research/market-research/.env and its safe local .env.example. Confirmed
research sender is included; only nonsecret server/port/TLS starting values were
copied. Own SMTP username/password and all future SMS gateway values are blank.
No existing app credentials were duplicated or printed. The actual software/.env
was verified byte-for-byte unchanged, including its old unused research entry.
Removed only this task's optional research block from software/.env.example after
verifying its prefix matches HEAD, restoring the original safe app example.

Changed the runner's configuration reader to this experiment's explicit .env
only; no parent-file or process-environment fallback and no new Python script.
Missing own credentials are reported as a production blocker without preventing
read-only TLS/DNS inspection. Mocks never load/use real SMTP or SMS credentials.
Updated the active README/context/allowlist to the independent layout; earlier
shared-env descriptions above remain historical and are superseded.

Nine direct checks pass: exact research path, no environment fallback, secret-free
reports, config provenance, missing credentials/config behavior, no copied secrets,
unchanged app .env and unchanged contact CSV. Private before/check records are in
data/task105-env-isolation-before.json and data/task105-env-isolation-checks.json.
Preserved the older readiness report as data/email-readiness-before-env-isolation.json
before refreshing the report from independent settings. No AUTH, real email/SMS,
Android setup, actual contact change, dependency, service, commit or push action.

The refreshed independent-config probe completed with TLS verified, SPF published,
DMARC absent, DKIM/sender permission unverified and own credentials missing (four
reported blockers). Final syntax/ignore/30-link/whitespace checks pass; app .env
and canonical CSV hashes match the before-state. App example matches HEAD.

## Git publication

The owner now explicitly authorizes committing and pushing the completed work
to master. Publish only reviewed source, fixed templates, the safe research
.env.example and documentation, including the deferred Task 104 planning record.
Keep actual credentials, contact CSVs, schedules, evidence, recovery archives,
capture tools/results and the research environment ignored. This authorization
does not enable production email/SMS or change services, DNS or contact data.
