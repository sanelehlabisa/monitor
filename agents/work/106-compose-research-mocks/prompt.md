# Task 106: Research Compose mocks

## Outcome
One independent Compose command starts Mailpit and a mock SMS HTTP API for
fictional outreach tests. Keep all implementation and generated captures inside
software/research/market-research/. Existing app Compose files stay untouched.

## Questions and answers
- The owner requests local mocks only, not production sending or an Android gateway.
- Reuse the existing research directory and approved two-script design. Add a
  server mode to send_due_messages.py rather than another Python source file.
- Keep the sender as a one-pass command; only the capture services stay running.
- No unresolved product questions. Docker's Linux engine was unavailable during
  inspection; it must be running before actual container verification.
- The owner explicitly approved Task 106 on 22 November 2026. Implementation
  authorization is limited to the scope below.

## Scope and reuse
1. Add docker-compose.yaml, a small mock-service Dockerfile and a restrictive
   .dockerignore inside market-research. Use a distinct Compose project, pinned
   images and loopback-only host ports: Mailpit web 8026, SMTP 1026, SMS API 8086.
   Check availability before starting; do not stop conflicting processes.
2. Use Mailpit strictly as a capture service, without SMTP relay/forwarding.
   Keep mock services on an isolated internal Docker network. No real credentials,
   private CSVs or the parent research directory may enter the build context or
   service mounts. Mount only dedicated ignored Mailpit/SMS capture subdirectories
   for persistence. Do not change either actual .env or require new secret values.
3. Extend the existing runner with a standard-library mock SMS server mode:
   health, bounded JSON message submission, accepted-message inspection and
   controlled local failure responses. Store only fictional captures below
   data/local-test/. No SIM, Android adapter, external forwarding or new framework.
4. Add an explicit local-test option for the runner to call the loopback SMS API;
   preserve the existing offline mock by default. Reuse send_sms and existing
   CSV locks, atomic writes, due selection, daily limits, templates and reporting.
   Permit no arbitrary gateway hosts or redirects. Preserve sent states and
   manual-review holds for uncertain acceptance; no automatic resend on timeout.
5. Verify using a fresh fictional fixture under data/local-test/, separate from
   the canonical contacts.csv and the owner's existing ready fixture. Preserve
   every real contact, scheduled date, source and credential byte.
6. Extend the source allowlist only for reviewed Compose/build files. Update the
   research README with start, send, inspect and stop commands, and the context
   with actual results. Record implementation/reuse/checks in changes.md.

## Verification
- Validate Compose configuration and build isolation; confirm only loopback host
  bindings, no real credentials/mounts, no relay and no external mock network.
- Start only this new mock project after approval; leave it running for the
  owner's testing. Inspect existing application files/services without changing
  them. Do not restart Docker Desktop or other stacks.
- Send fictional email and SMS through the existing one-pass runner and verify
  actual Mailpit/API captures, exact templates and immediate CSV outcomes.
- Check controlled failures, outside-hours/weekends, future dates and daily caps.
  Repeat the runner and restart the mock project: sent rows produce no resends
  and accepted captures persist. Check ambiguous HTTP outcomes remain held.
- Confirm real contacts, both .env files and original app Compose hashes remain
  unchanged; private captures/data stay ignored. Report any unavailable checks.

## Exclusions
No real email/SMS, production activation, Android installation, new scraping,
DNS changes, recurring sender jobs, app changes, contact edits, commit or push.
