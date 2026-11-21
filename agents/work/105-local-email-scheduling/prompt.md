# Task 105: Local email and SMS scheduling

## Outcome
Implement the owner's email Tickets 1-4 plus the SMS extension in one lightweight
CSV workflow: setup checks, local SMTP capture, an offline SMS mock, a repeatable
runner, per-channel reporting and a saved schedule. Preserve collection/import
behavior and the exact email template. Stop before real email or SMS delivery.
Status: complete within the approved local-only scope; real delivery remains disabled.
The subsequent owner-requested two-script/CSV-date correction is recorded in
[simplify-prompt.md](simplify-prompt.md) and supersedes the earlier helper/scheduler
file layout and code-level November expiration. The owner subsequently requires
an independent market-research/.env; that supersedes the original shared-env
layout below, with existing app .env preserved unchanged.

## Questions and answers
- Confirmed research sender: sanele.hlabisa@roventics.com. Reuse the one ignored
  software/.env and its SMTP keys; preserve app EMAIL_FROM=info@roventics.com and
  existing credentials. Research sender permission is not yet verified.
- Latest limits replace ten emails/day: target exactly five per channel/weekday,
  hard maximum six per channel/day, 09:30-15:30 Africa/Johannesburg. The original
  23-30 November 2026 experiment remains: 23-27 and 30 are its six weekdays.
- Current CSV has 643 email rows and 1,499 phone rows with no person/group links
  or named people. Phone metadata: 1,391 mobile, 107 fixed-line and one VoIP; it
  does not establish SMS capability, ownership or email absence.
- Asked the owner how to confirm cross-channel links. Proposed minimal policy:
  add a manually assigned contact_group. Keep unconfirmed phone rows unscheduled.
  A confirmed complete phone-only group can use SMS; any email in a group takes
  priority, even if not due or failed. No inferred links from domains, filenames,
  adjacent excerpts or shared university publishing sites. This conservative
  grouping/hold policy is included in the owner's approval.
- No automatic email-to-SMS follow-up. A reply/contacted/sent state anywhere in
  a confirmed group blocks another initial contact. Positive replies are manual.
- Keep due<=now catch-up inside working hours and per-channel caps; no sends on
  weekends, outside working hours or outside this experiment. The approved due
  rule uses bounded catch-up, without a backlog burst.
- DKIM selector is unknown: report unverified, not passed/missing by assumption.
  Docker CLI is present but its engine was unavailable. Actual Mailpit capture
  requires Docker running or an existing native service, not mocks alone.
- Task 104/survey work is deferred. No survey link, individual email variants or
  LLM-generated messages. No Android gateway download, install or configuration.

## Scope and reuse

### 1. Read-only outbound readiness
- Inspect sender, SMTP host/port, credential presence, TLS and public SPF/DKIM/DMARC
  with bounded checks. Use EHLO/verified TLS if available; no AUTH or message
  submission to real SMTP. Unknown DNS/selector/sender permission remains explicit.
- No DNS or provider changes, secret exposure, real test emails or app changes.
  A private readiness report lists blockers before later production approval.

### 2. One CSV contract and contact priority
- Preserve original rows, IDs, context, notes, legacy/contacted/response fields
  and normalized (contact_type, contact_value) identities. Do not merge methods.
- Append email plus email_status/email_scheduled_at/email_sent_at/email_attempts/
  email_last_error, and phone plus sms_status/sms_scheduled_at/sms_sent_at/
  sms_attempts/sms_last_error. response_status and notes already exist.
- Add email_last_attempt_at and sms_last_attempt_at for restart-safe daily budgets,
  plus the proposed manual contact_group. No generic duplicate send-status fields.
  Mirror only the row's actual method into email/phone; do not invent missing data.
- Reuse CSV validation, single writer lock and guarded atomic saves from pipeline.py.
  Support the current 15-column and approved expanded header; preserve unknown
  schemas. Collector upserts must retain new state without a crawl/evidence replay.
- Select email first where it exists in a confirmed group. SMS requires a manually
  confirmed phone-only group; blank/unknown groups remain unscheduled for SMS.
  Landline/uncertain entries remain intact, without automatic SMS scheduling.
- Suppress already contacted/sent/replied/opted-out groups and duplicate method
  identities. Never send .ac.za emails. Do not switch to SMS after failed or
  unanswered email. Schedule at most one initial method per confirmed person.

### 3. Shared one-pass runner and state
- Use a small shared channel runner with few CLI entrypoints; preserve email
  behavior and reuse the same scheduling/state helpers for SMS. No app framework,
  queue, database, daemon or recurring-job installation.
- Each run reads current time/CSV, counts today's per-channel successes and
  reserved attempts, selects currently due eligible rows, persists each attempt,
  reports and exits. Check time limits before starting each submission. Outside
  hours/weekends, report zero due and do not submit or mark attempts.
- Target five/day; never exceed six attempted contacts/channel/day. Allow at most
  one automatic attempt/contact/channel/day and three total safe attempts. UTC
  attempt timestamps make restarted invocations respect those limits.
- Use new/scheduled/sent/failed/skipped plus a transient sending state. Before a
  submission, save sending, increment that channel's attempts once and record its
  attempt timestamp. On confirmed acceptance save sent/sent_at immediately; on
  known failure save the channel error/outcome and continue safe other contacts.
- Retry only explicit temporary rejection/no-acceptance outcomes within limits.
  Permanent failures become failed. Interrupted sending or uncertain acceptance
  is held for manual review, never automatically resent. SMTP QUIT failure after
  known DATA acceptance must not undo success. A stable message ID aids audits,
  but cannot prove remote exactly-once delivery.
- Failed persistence stops further submissions; conflicting/stale writer locks
  produce an explicit error. Do not reset or guess delivery state on restart.

### 4. Local transports only
- Email: exact template below, one recipient, real isolated Mailpit capture bound
  to loopback, no relay/forwarding and no production credentials. Use synthetic
  .invalid recipients/test CSV only; reject actual contacts.csv as delivery input.
  Do not restart app services. Record actual captures before owned test cleanup.
- SMS: expose a small typed send_sms(phone_number, message) boundary with a local
  mock returning/capturing results and controllable test failures. It performs no
  HTTP request, invokes no Android tools and sends nothing to a handset/carrier.
- Document optional future SMS_GATEWAY_URL, SMS_GATEWAY_USERNAME,
  SMS_GATEWAY_PASSWORD and SMS_GATEWAY_API_KEY in the existing environment example.
  No actual gateway values or implementation yet. Populating URL/credentials must
  not activate a real adapter; unsupported real SMS delivery fails closed.
- Mock successes update only synthetic test CSV, never real contacted/sent state.
  Reports clearly identify local/mock mode. Keep one exact SMS body; no links.

### 5. Save the initial schedule
- Provide preview and explicit apply, stable ID order, idempotent assignment.
  Preserve existing reservations; keep overflow unscheduled. Store aware UTC,
  display local time. No randomized behavior is necessary.
- Six weekdays, target five slots/channel/day: 09:30, 11:00, 12:30, 14:00, 15:30
  local (07:30, 09:00, 10:30, 12:00, 13:30 UTC). At most 30 initial emails and
  30 confirmed phone-only SMS contacts, never duplicate a person's channels.
- With current data, email capacity is 30 of 643 (613 stay unscheduled); real SMS
  capacity stays unallocated until contact links/phone-only confirmation exist.
  Demonstrate both channels with confirmed synthetic groups.
- After local tests, safely migrate/save the real canonical CSV schedule only.
  Actual contacts retain zero attempts and no sent/contacted updates. Produce a
  private schedule proposal/audit; bulk addresses/numbers never enter Git or chat.

### 6. Per-run reporting
Print these counters for the selected CSV, with local/mock mode made explicit:

```text
Emails sent today:
SMS sent today:
Emails sent this run:
SMS sent this run:
Email failures:
SMS failures:
Remaining email contacts:
Remaining SMS contacts:
```

Count logical messages, not a claim of physical delivery or carrier SMS segments.
Show held/unconfirmed SMS candidates separately so zero eligible SMS is clear.
Keep audit logs private; the CSV remains the single delivery-state source.

Email subject: Electricity management in student accommodation

```text
Hi,

I’m currently researching how student-accommodation providers manage electricity usage across their properties.

I would like to better understand the challenges operators experience and would appreciate the opportunity to ask you a few short questions.

Would you be open to sharing your experience?

Kind regards,
Sanele
Roventics (Pty) Ltd
```

SMS body:

```text
Hi, I'm Sanele from Roventics. I'm researching how student-accommodation providers manage electricity usage across their properties. Would you be open to answering a few short questions?
```

## Verification
- Real isolated Mailpit capture and offline SMS mock, using fictional data only.
  Verify both exact templates, success/failure state writes, repeated invocation,
  already-sent/group suppression, email-first behavior, confirmed phone-only
  eligibility, unconfirmed hold, replies, no fallback/follow-up and no real adapter.
- Test before/after hours, weekends, local/UTC dates, catch-up, pre-existing daily
  counts, six/channel hard caps, independent budgets, bounded retry and interrupted
  sending. Simulate SMTP accepted-then-QUIT-error and unknown acceptance safely.
- Verify writer conflict, failed/external CSV writes, migration/legacy preservation,
  idempotent schedule assignment and no test delivery from the canonical CSV.
- Show the proposed six-day schedule and actual local behavior before activation.
  Record evidence/results in changes.md. Use temporary direct checks by default;
  no persistent test files, real recipients, secret dumps or pretend test results.

## Exclusions
No real email/SMS, Android app/SDK/gateway download/install/configuration, live HTTP
SMS adapter, automatic follow-up, inbox polling, DNS changes, task installation,
long-running processes, databases/Celery/Redis/queues/web UI, LLM copy, survey
work/link, app/service restart, new scraping, unrelated cleanup, commit or push.

References: [Python SMTP](https://docs.python.org/3.14/library/smtplib.html),
[Mailpit capture](https://mailpit.axllent.org/docs/configuration/smtp/),
[SMTP acceptance ambiguity](https://www.rfc-editor.org/rfc/rfc5321#section-6.1).
