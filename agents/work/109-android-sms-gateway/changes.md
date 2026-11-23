# Task 109 preparation

The owner reports real email success and asks for concise Android gateway setup.
Read-only canonical counts confirm five email attempts/sent rows, zero SMS sent/
scheduled and zero confirmed real phone-only groups. No contact/config changes.
Do not repeat the earlier unsent reset: existing email history is now real.

Inspected the runner: its loopback SMS mock uses a different payload/path and
real SMTP mode currently excludes SMS. Updating gateway .env keys alone cannot
enable actual SMS. Reviewed official SMSGate installation/local-server/API docs
and the official release page. The suggested route is owner-installed standard
APK, Local Server, same trusted Wi-Fi, Basic Authentication and singular /message.
No provider app, file or Android package was downloaded/installed by the agent.

Prepared prompt.md from agents/prompt.md for a small SMSGate-specific adapter in
the existing sender, independent channel selection and preserved CSV safeguards.
Updated current context and the existing 71.10.6 roadmap entry. No implementation,
network call to the phone, credential edit, real message, service operation,
commit or push. Implementation awaits Task 109 approval; phone endpoint details
and secrets remain for the owner to configure locally.

## Approved implementation

The owner installed/configured the app, entered its URL/username/password in
the private research .env, then explicitly approved Task 109. No API key or
Device ID is required for Local Server Basic Authentication. Did not alter .env,
working SMTP settings or canonical contact/email history.

Read-only phone documentation returned /docs/index.html and its Swagger schema.
The installed schema and current official public schema use POST /messages,
textMessage.text, a one-entry phoneNumbers array and HTTP 202 GetMessageResponse.
The older getting-started example uses singular /message. Base URLs now use
/messages automatically; explicit legacy paths are left literal with no POST
redirect following or retry fallback. Provider success is confirmed through the
queued receipt, not inferred from arbitrary 2xx responses.

Extended send_sms in the existing sender with SMSGate Local Server transport,
Basic auth from the three existing environment keys and stable message IDs.
No API key/Device ID field or SDK. Only private Wi-Fi IPv4 endpoints are permitted;
public addresses/hostnames, embedded credentials, query/fragment routing and
untrusted paths are rejected. HTTPS keeps certificate verification. Direct
http.client connections use no proxy or automatic redirects. Logs/errors never
echo credentials or provider message bodies.

HTTP 202 receipts must match the submitted ID, destination and expected state/
device fields. Explicit rejection is safely failed/bounded; disconnect, malformed
receipt, server uncertainty and existing-ID conflict remain held for queue review.
Queued receipts are tagged in the existing attempt log without a CSV field change.
Reused the five/day budget, locking/atomic writer, group/reply/suppression rules
and status transitions. No scheduling, identity inference or automatic follow-up.

--channel sms no longer validates or submits SMTP. The normal command can use
both real channels, while unconfigured mock channels never consume real contact
history. Mock fixtures cannot reach real transports, and the old local mock API
still works. Added read-only --check-setup --channel sms using the protected
/devices route and installed Swagger; docs alone may be public and are not used
as sole proof of authentication. Existing username/password authenticate correctly:
read-only /devices returns 401 without auth and 200 with configured auth.

Updated safe example/help, setup/run guide, research/root indexes and context.
Removed only the unused API-key line from the example; any actual private key
setting is left unchanged/ignored. Two Python source scripts remain; no new
dependency, schema/table, separate sender, Android download/install or service.

## Verification and limits

74 controlled checks pass, recorded privately in data/task109/verification.json.
An owned loopback fake server exercises the exact request/auth/receipt contract,
stable IDs, explicit paths, successful acknowledgement, rejection, timeout/
disconnect, invalid/mismatched/oversized receipts, redirects, TLS verification
and sanitized errors. No test POST reached the phone or cloud. Isolated test
canonical fixtures verify five/day, same-day restart/no duplicates, three safe
temporary attempts, permanent failure, unknown holds on later days, and mixed
email/SMS routing. Email transport is stubbed in mixed tests; SMS-only never
touches SMTP, even with invalid unrelated settings.

Read-only checks against the owner's actual private phone endpoint verify device
authentication and current Swagger. No message/inbox/queue operation was used on
the real phone. Public and device schemas/documentation were retained privately
under data/task109/; canonical/config baseline hashes are in before.json.

Canonical CSV and all configured .env/app/template hashes are unchanged. Five
real email attempts/sent rows remain intact. SMS sent/scheduled/confirmed-group
counts remain zero; the 917 phone methods are deliberately not auto-selected.
The SMS command now runs, but it sends nothing until the owner confirms eligible
phone-only/mobile records and supplies their SMS dates. The owner can test their
own number through the app's docs/UI before authorizing a real research batch.

No real email/SMS, contact/group/date edit, app/VPS restart, commit or push.

References: [Local Server](https://docs.sms-gate.app/getting-started/local-server/),
[current API schema](https://capcom6.github.io/android-sms-gateway/swagger.json).

## Owner-authorized activation

After running the sender, the owner explicitly requested marking all phone
numbers confirmed so they can be attempted. The earlier request to fix zero due
and align .env is part of the same steering. Recorded the amendment/scope in
activation-prompt.md and presented it before applying; it supersedes the earlier
no-grouping/scheduling boundary for this activation only. No guard was removed.

The gateway was already reachable; the blocker was 917 blank confirmation groups
and SMS dates. Under the shared lock, saved exact private CSV/config snapshots
at data/task109/activation/contacts.before.csv and research.env.before, then set
917 blank groups to stable per-phone owner-confirmed IDs and populated 917 blank
SMS dates with the activation UTC timestamp. This records the owner's permission
to try, not a claim of delivery, provider identity or proven SMS capability.

Normalized only SMS_GATEWAY_URL's path from the existing working base URL to
/messages. The private IP, port, Basic credentials, SMTP keys and application
settings are unchanged. Every email row and all non-target phone fields compare
exactly to the snapshot. Existing future dates/history would be retained; no
attempt/sent/reply/contact state was reset.

Reload/schema checks pass. Existing mobile-type validation leaves 839 eligible
and 78 non-mobile/unsupported records held. Read-only preview selects five SMS;
the five sent emails, their attempts and all SMTP values are preserved. A real
read-only device/docs auth check passes after endpoint normalization. SMS attempts
and sent stay zero: no live SMS or email was submitted by the agent.

Private counts, next IDs and before/after hashes are in
data/task109/activation/result.json. No files were deleted or added to the active
contact register outside the existing canonical CSV; snapshots remain recovery
evidence only. No code, daily-cap, service, commit or push change in this step.

## Owner live run and publication

The owner subsequently ran the sender and requests committing/pushing to master.
Read-only canonical review now shows five sent emails and five SMS attempts/
accepted rows, zero SMS failures and zero uncertain states. This is owner-run
live evidence; the agent did not submit messages. Accepted gateway receipts do
not prove handset delivery. Do not reset or replay these records.

Publish reviewed code, safe .env.example, instructions and work records only.
Actual .env, contacts, queued receipts, captured schemas, activation snapshots,
audits and generated data remain private/ignored. No further sending, config
edit, contact change or service restart is part of publication.
