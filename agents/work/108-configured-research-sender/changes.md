# Task 108 preparation

Inspected current runner, CSV state, configuration examples, Compose mocks and
agent instructions. Normal invocation is still read-only; the only SMTP adapter
is loopback/fictional-only. Daily cap is six and weekdays/hours are enforced.
The independent research configuration exists; application settings stay separate.

Prepared prompt.md from agents/prompt.md for one configured SMTP flow, a hard
five/day/channel cap, no weekday/hour gate, local date-based due selection and
.env-controlled CSV/transport selection. Safe defaults use a fresh fictional
fixture so Mailpit tests cannot mark real contacts as contacted. Live SMS is not
specified because no gateway/API has been selected. Two source scripts remain.

The owner's current request authorizes preparing this concrete implementation
scope; AGENTS.md requires approval of the new prompt before building. Added the
roadmap/current-context entry. No source/config/data/service change, message,
network request, commit or push was performed in Task 108 preparation.

## Approved implementation

The owner approved Task 108. Reused the two Python sources, one existing CSV
state machine, fixed templates, lock/guarded atomic writer and capture services.
No new Python script, settings module, scheduler, dependency or framework.

send_due_messages.py now reads this experiment's explicit .env. Normal invocation
delivers and exits; --preview/--report remain read-only. CONTACTS_CSV selects a
fresh fictional default at data/local-test/task108/contacts.csv. Loopback SMTP
refuses the canonical CSV/real provenance; real SMTP refuses mock history and
uses only the owner-selected canonical register. Simulated clocks cannot submit
live mail. Research .env/example now select Mailpit 127.0.0.1:1026 and local SMS
capture. The confirmed research sender/account fields are preserved; original
configuration is recoverable at private data/task108/research.env.before.

Implemented authenticated SMTP with verified implicit TLS or mandatory STARTTLS
for non-loopback hosts. Host is supplied to the constructor for correct TLS
hostname/SNI verification. Local mocks never receive account credentials. SMTP
error text is sanitized, explicit rejections are bounded, ambiguous DATA remains
held, and accepted DATA survives failed QUIT. Added a normal Date header while
retaining the exact approved message templates. No real SMTP login or mail was
performed during verification. DNS/provider/signing inspection remains optional;
it is not an automatic delivery approval or DNS-edit operation.

Hard cap is five attempted contacts/channel/local day, including failures and
reserved submissions, across repeated invocations. Removed weekday/hour gates;
saved UTC timestamps compare by Johannesburg calendar date, so same-day clock
times no longer delay a morning run. Future dates wait, blank dates hold. No
schedule allocation or canonical date/group/history changes. SMS remains local
or offline mock only; real-SMTP mode sends email and rejects explicit live SMS.
No Android gateway/provider contract was invented or installed.

Consolidated the active README and context, preserving application facts and
historical work records. Earlier local walkthrough flags share the same loop;
no parallel production script. Existing useful source, captures, native tool,
research files and recovery were retained; no files were retired/deleted.

## CSV file-access correction

A fictional failure test encountered the same OS-level CSV save failure seen in
Task 106. It stopped safely; its interrupted state/captures remain unchanged at
data/local-test/task108/failures/. The OS cause is unverified. Added at most three
PermissionError retries to the existing guarded_write helper, with 0.1-second
delays and a fresh original-content check before each retry. Persistent errors
still stop; external edits are never overwritten. These retries only retry file
persistence, never an uncertain network submission. A separate fresh v2 fixture
then passed actual SMTP/API rejection, cap and restart checks. No new crawl logic.

## Verification

Private report: data/task108/verification.json; 60 checks pass.
- Actual normal command used .env with a separate fictional fixture: five emails
  captured in Mailpit and five HTTP SMS captures, exact templates; a fresh process
  sent zero again. Next local day sent only the remaining two/channel. Owner
  default 10-email/10-phone fixture remains fresh and unsent.
- Controlled SMTP doubles verify STARTTLS before AUTH, implicit TLS, certificate/
  hostname checks, missing TLS, bad certificates/auth, sanitized errors, DATA
  rejection/disconnect and failed QUIT after known acceptance. No real provider
  was authenticated, so actual mailbox permission/signing remain unverified.
- Actual local failure runs verify five attempted-contact caps including failures,
  continuing other contacts, uncertain SMS holds, no repeated success/unknown
  submission, three safe attempts maximum, concurrent-lock rejection and local
  midnight rollover. Early Sunday/late-night, same-day, blank and future dates pass.
- File-write doubles verify transient permission recovery, three-attempt bound
  and preservation of an external edit made between retries. Original interrupted
  fixture was not reset to force a passing test.
- Protected hashes cover canonical contacts.csv, application .env/both Compose
  files and both templates. Research configuration's original account values are
  preserved privately. All artifacts/configuration remain ignored.

Existing capture services were used; no real contact, phone group or live state
was changed. No real email/SMS, recurring task, new crawl, app/VPS operation,
commit or push.

Final checks verify inherited SMTP/CSV environment variables are ignored,
credential-encoding errors stay sanitized, the owner fixture remains unsent and
all protected hashes still match. Syntax, two-script layout, relative links,
whitespace and private-output ignore checks pass. The final mock image builds
successfully and only the research SMS service was recreated; it is healthy with
persisted captures. Mailpit remains running. Normal --preview shows five eligible
fictional contacts/channel, and --check-setup confirms mock selection without
authentication or sending.

SMTP implementation reference: [Python smtplib](https://docs.python.org/3/library/smtplib.html).
No DNS, inbox delivery or actual provider authentication/signing was validated;
those depend on the owner's chosen account/settings.

## Publication authorization

The owner asks to commit and push the completed work to master, then stop for
the day. Include Task 107 source-free cleanup records and Task 108 reviewed
sender/source/documentation changes. Only public source, instructions and the
safe .env.example are published; actual .env, cleaned CSV, fixtures, source
evidence, captures and recovery remain ignored. No live account authentication,
message, additional contact edit or service operation is authorized by this Git
publication. Final review reconfirmed 60 recorded checks and protected hashes.

The owner also requested all contacts be unsent because earlier delivery was
mock-only. Verified zero attempts/sent/contact dates and no pending/error fields.
Normalized 30 email statuses from scheduled to new under the shared lock; all
1,560 canonical methods are now new/uncontacted in their relevant channel, with
the irrelevant channel skipped. Saved sending dates remain intact. A fresh private
snapshot and before/after hashes are under data/task108/contacts.before-unsent.csv
and unsent-reset.json. This owner-authorized final status change supersedes the
earlier canonical hash baseline; all other fields stay intact. Read-only preview
for the first scheduled date still selects five emails and zero SMS. Mock history
stays separate; no messages were submitted.
