# Task 056: Database and access refocus plan

## Result

Approved planning only; zero changed implementation lines. Added stable Ticket
69 with seven modular subtickets and explicit dependencies/acceptance:

- 69.1: existing-data audit, minimal target schema and backup/restore evidence.
- 69.2: fresh schema.sql/seed.sql and persistent Docker initialization/reload.
- 69.3: DB-only user/admin authority, fresh admin seed and no admin env fallback.
- 69.4: membership authorization and transactional last-member protection.
- 69.5: minimal sharing UI, membership-aware My/All and scoped email search.
- 69.6: fixed monthly planning date, distinct from predicted run-out.
- 69.7: day-before monthly emails, all meter members and recipient-level dedupe.

Created separate Ticket 70 for readable HTML OTP/reminder messages with plain-
text fallback and safe app links. Extended existing future 68 for guest/local
device storage without login versus authenticated account/shared storage; no
framework, transfer/sync or notification implementation is selected.

## Confirmed policies and boundaries

- Signup remains open and creates regular users. DB type will become the sole
  role authority; fresh seed hlabisasanele730@gmail.com as admin with full access.
  Later role changes are manual DB edits, not restart-time promotion or an email
  override. Remove active admin env dependencies in 69.3, not this planning task.
- Nine target domain tables means existing eight plus membership. Preserve
  secure auth fields, UTC occurrence/audit times, separate reminder settings/
  deliveries and per-meter derived rates. No forecast replacement or stored
  consumption-rate source of truth was introduced.
- Plan to the 1st and email the day before, to every member of that meter without
  individual opt-in; global admin scope alone is not email membership. Retain
  low-balance eligibility and the finite runner/SMTP. Target-cycle, timezone,
  per-recipient retry/dedupe and membership-removal checks are explicit.
- Data preservation, isolated restore verification and explicit upgrade/reset
  approval precede any transition. Fresh-volume initialization cannot upgrade
  existing data. Keep compatible schema/API paths until dependent sharing code
  is ready; no intermediate broken-app cutover.
- Whole-meter deletion, creator display, sharing onboarding, saved timezone/send
  time/catch-up policy and future mobile storage/sync decisions remain for their
  implementation prompts. They are not invented defaults or blockers to logging
  the plan. Every implementation still needs separate approval.

## Documentation and reuse

Updated root/software/backend/database/frontend READMEs and agents/context.md.
Root owns the short ordered roadmap; nearest component READMEs own detailed
acceptance. Current one-owner/env-admin/opt-in behavior is labelled separately
from the planned changes. AGENTS.md and rules.md were read and retained: their
existing workflow/boundaries still apply. Removed only superseded prospective
guidance; historical work records, completed IDs and research stay intact.

Reused current Psycopg SQL, OTP/cookie session contracts, meter/ledger APIs,
single forecast boundary, finite runner, SMTP/delivery claims, compact MUI and
existing Tickets 55/65/66/68. No new architecture, service or dependency.

## Verification actually run

- PASS: root definitions of 69, 69.1-69.7, 70 and 68 each occur exactly once.
- PASS: all 32 local Markdown links in the six changed docs/prompt resolve;
  explicit new-file whitespace and git diff --check pass.
- PASS: independent cross-document review of IDs, dependencies, role authority,
  signup, recipients, calendar boundaries, UTC and current/planned distinction.
- PASS: changed tracked paths are exactly the six approved Markdown documents;
  untracked work is limited to this prompt.md and changes.md. Runtime/frontend
  code, SQL/migrations, research, Docker/env configuration, refocus.md and earlier
  work records have no diffs. No .env edit, data/service action, email send,
  commit or push was performed. No application suite was run for documentation.

Next priority is 69.1. Next work number is 057, requiring a new approved prompt;
no follow-on implementation has started. Task 056 was uncommitted at this
verification point. The user subsequently authorised its commit/push together
with the earlier local research commit; Git history records the final handoff.
Next-batch preparation starts with 057/69.1, not an automatic database cutover.
