# Task 105 correction: Two scripts and CSV-controlled due dates

## Outcome
Apply the owner's direct correction within approved Task 105: keep two Python
source files in this research folder, pipeline.py and send_due_messages.py.
The runner reads existing CSV send dates, decides what is due at invocation,
respects local hours/weekday/channel caps, updates local-test outcomes and exits.
Real email/SMS remain disabled pending the separate approval already required.

## Questions and answers
- The owner explicitly requests one or two scripts and due-date selection from
  the CSV. Existing reservations are already saved; do not generate them at runtime.
- Keep two files total: preserve collection/import in pipeline.py and consolidate
  outreach state, reporting and read-only setup inspection into the runner.
- CSV dates, including overdue dates, are authoritative. Remove the unrelated
  hardcoded November expiration fence, without changing any saved send dates.
- Existing email-first grouping, SMS mock, per-day limits and test-only safeguards
  remain within the approved scope. No additional clarification is necessary.

## Scope and reuse
1. Reuse existing functions by moving them into send_due_messages.py; eliminate
   runtime helper-module dependencies and schedule allocation code. Bare invocation
   checks current CSV/time and shows due candidates safely while real delivery is
   disabled. Existing --local-test, --report and --check-setup remain optional modes.
2. Eligibility uses saved channel scheduled_at <= current aware time, weekday and
   working-hour checks, existing contact/sent state, priority and daily caps.
   Future/blank dates are not due. A saved date on an eligible new/scheduled row
   is sufficient; clearing it holds the row without another status edit. Never
   create/reschedule rows during a run.
3. Retire outreach.py, schedule_messages.py and email_readiness.py after dependency
   checks and verification of their private recovery snapshot. Preserve all data,
   current reservations, templates, state fields and historical reports. Record
   exact paths in changes.md. Keep original approved local-only delivery gates.
4. Update the source allowlist, concise usage instructions and active context.

## Verification
Check future/past/same-day CSV dates, later dates beyond the old window, weekends,
hours, day caps, repeated invocation, state preservation, email/SMS priority and
local/mock restrictions. Verify both source files parse/import, no active imports
reference retired helpers, default invocation is safe, original CSV hash is
unchanged, recovery is valid and private data remains ignored. No new real sends,
Android/service operations, installation, commit or push.

## Exclusions
No new contacts, schedule allocation, production activation, live gateway, message
changes, schema changes, dependency additions, new recurring process or app work.
