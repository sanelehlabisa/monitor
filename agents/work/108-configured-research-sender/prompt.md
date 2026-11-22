# Task 108: Configured research sender

## Outcome
One normal sender command reads the research .env, sends due contacts, saves each
outcome and exits. Default configuration uses Mailpit and fictional data; changing
only .env enables real SMTP with the canonical CSV. Five/day/channel, any hour.

## Questions and answers
- The owner requests real SMTP functionality, Mailpit defaults, no working-hour
  restriction, a simple main command and fewer scripts/files.
- Keep the existing two Python scripts: collector and sender. No third sender,
  scheduler, settings module or new service/framework.
- Daily hard cap is five attempted contacts per channel, shared across repeated
  runs. Remove hour/weekday gates. Saved dates still control eligibility: use the
  local calendar date, so a same-day scheduled contact need not wait for its old
  clock time. Future dates wait and blank dates remain held.
- Use CONTACTS_CSV in this experiment's .env: a fresh fictional fixture by default,
  data/contacts.csv for real SMTP. This prevents mock success from consuming the
  real contact history. Switching transport/data requires .env edits, not code.
- Sender remains sanele.hlabisa@roventics.com. No real email is authorized during
  implementation/verification; use captures and fictional data only.
- An Android gateway/API has not been selected. Keep SMS local/mock-only; do not
  invent a live provider contract or install/configure Android software.
- The owner explicitly approved Task 108; implementation is authorized within
  this scope, with fictional captures only during verification.

## Scope and reuse
1. Reuse the existing runner, fixed templates, CSV contract/lock/atomic saves,
   eligibility/group protections, reports and ambiguous-acceptance holds.
   Make the normal invocation perform delivery; keep an explicit read-only view.
   Read only market-research/.env, never the app .env or inherited SMTP secrets.
2. Implement SMTP using existing research keys: host, port, secure, username,
   password and sender. Allow unauthenticated plaintext only for loopback Mailpit;
   require verified TLS (implicit TLS or STARTTLS) and complete credentials for
   non-loopback SMTP. No silent downgrade or secret-bearing error/log output.
   Known DATA acceptance stays sent even if QUIT fails; ambiguous acceptance is
   held for manual review. Preserve bounded retries and per-attempt safe saving.
3. Use one delivery/state loop for mock and configured SMTP. Set the hard cap to
   five for each channel and count stored attempts/successes on the local day.
   No daemon, sleep-until-due loop or automatic follow-up. No automatic schedule
   allocation or change to existing canonical dates/groups/state.
4. Update only the independent research .env/example for safe Mailpit defaults
   and CONTACTS_CSV. Preserve any current account values in private recovery;
   never copy credentials into containers. Local mock delivery must refuse the
   canonical CSV and require fictional provenance. Real SMTP uses the canonical
   CSV only when the owner selects it. Simulated clocks must not enable live mail.
5. Keep the same Compose capture services, editable message files and two Python
   sources. Reuse the existing SMS API boundary for mocks only. Simplify redundant
   command/config options and README instructions; do not remove useful source,
   private research, recovery, unique captures or user files just to reduce count.
6. Update README/context and record actual changes/reuse/checks in changes.md.
   DNS/TLS readiness inspection may remain optional; do not alter DNS or perform
   real authentication/submission during this task.

## Verification
Use a fresh fictional CSV with the normal command and actual Mailpit/SMS captures.
Verify default .env operation, five-per-channel cap across reruns/process restarts,
midnight rollover, weekends/any-hour operation, same-day/future/blank dates,
exact templates, immediate state saving and no duplicate successful submissions.
Exercise TLS/auth success/failure branches with controlled local doubles, not
real account authentication. Verify safe failures and ambiguous DATA holds.
Hash-check canonical CSV/app configuration; no real schedule/status changes.
Confirm only research capture services are used, secrets stay ignored, and .env
switching is documented without pretending a live SMS adapter exists.

## Exclusions
No real emails/SMS, live gateway, new scraping, DNS/app changes, automatic task
installation, canonical contact edits, third Python script, commit or push.
