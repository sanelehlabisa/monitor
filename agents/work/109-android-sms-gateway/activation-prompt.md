# Task 109 amendment: Activate SMS eligibility

## Outcome
Apply the owner's explicit confirmation to the phone rows, give unscheduled SMS
records a due date and make the configured device endpoint explicit. The owner's
next sender invocation may attempt up to five, using the existing daily budget.

## Questions and answers
- The owner says to mark all numbers confirmed so sending works, accepting that
  delivery can only be established by an attempt. This explicitly supersedes the
  earlier no-grouping/scheduling restriction for this activation step.
- This records owner-approved eligibility for an attempt, not proven delivery or
  a guessed name/organisation. Use distinct stable phone groups where blank.
- The earlier request to fix zero SMS and update .env covers making currently
  blank SMS dates due today and normalizing the current working base URL to the
  installed API's /messages path. Preserve explicit future dates/known groups.
- Five/day, sent/reply/suppression checks and mobile-capability validation stay
  in place. Never reset the five already sent emails or existing SMS history.
- No real SMS is sent by the agent; the owner reruns the supplied command.

## Scope and reuse
No new code or script. Snapshot the canonical CSV and independent research .env
privately, then use the existing CSV lock, schema validation and guarded atomic
save. Fill blank contact_group on phone rows with stable per-row identifiers;
fill blank sms_scheduled_at on untouched phone rows with today's UTC timestamp.
Do not erase attempts, sent/contact dates, replies, suppression or future dates.
Update only SMS_GATEWAY_URL's path in the research .env, retaining the working
private address/port, username/password, all SMTP values and application settings.

## Verification
Reload and validate schema/unique identities. Compare every email row and all
non-target fields to the snapshot. Run only read-only SMS setup/preview/report
commands: authenticate on device/docs routes, show up to five due, and verify
SMS attempts/sent stay zero. Preserve a private before/after audit and update the
README/context/changes record. Known non-mobile types remain held by existing code.

## Exclusions
No actual messages, code/guard removal, identity inference, app/router/service
changes, Android installation, commit or push.
