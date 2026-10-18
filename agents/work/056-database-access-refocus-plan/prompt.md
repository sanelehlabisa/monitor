# Task 056: Database and access refocus plan

## Aim

Create small, ordered roadmap tickets for the database/access refocus without
changing the running application or existing data.

## Clarifications

- Keep email-OTP signup open and reuse secure cookie sessions.
- Store user/admin types in the DB; seed hlabisasanele730@gmail.com as admin
  with full access. Manage later admin promotions directly in the DB. Remove
  admin environment configuration in that implementation, with no env fallback.
  New signups default to user. Admin seeding is fresh-setup only, never a runtime
  email override or restart action that undoes a manually changed role.
- Use the 1st as the fixed monthly planning date, separate from predicted
  run-out. Send the monthly email the day before. Reminder recipients are every
  member of that meter, not every account in the system. No per-member opt-in or
  weekly/monthly schedule selector now; retain low-balance eligibility rules.
- Add a separate HTML-email ticket with readable messages and links to the app.
- Future mobile/local-only use needs no login; account storage requires login.

## Change

- Add Ticket 69 with modular subtickets, dependencies and acceptance checks:
  - 69.1: Existing-data audit, backup/restore and minimal target-schema review.
  - 69.2: Fresh schema.sql/seed.sql, persistent Docker initialization and reload.
  - 69.3: DB-only roles, admin seed and removal of admin env dependencies.
  - 69.4: Membership persistence and backend authorization/last-member guard.
  - 69.5: Minimal sharing UI/API integration, including My/All and email search.
  - 69.6: Fixed first-of-month planning date, keeping 30-day quantities/run-out.
  - 69.7: Day-before monthly delivery and shared-member email recipients.
- Plan nine domain tables by retaining existing names and separate reminder
  settings/delivery records, adding membership. Preserve OTP/session digests,
  expiry/abuse controls, session user links and ledger occurrence/audit times.
  Consumption rates stay derived per meter, not a second source of truth.
- Every member may manage readings/membership; prevent last-member removal,
  including concurrent removal/account-deletion paths. Mark whole-meter deletion,
  creator display, sharing onboarding and saved timezone/send time as decisions
  to settle in the relevant implementation prompt, not invented new features.
- Cover fresh versus existing volumes, explicit safe upgrade/reset approval,
  per-recipient deduplication, membership removal and month/year boundaries.
  Keep low-balance warnings, the finite runner and SMTP; no new service.
- Add Ticket 70: HTML OTP/reminder emails, plain-text fallback and safe app links.
- Extend future Ticket 68 for guest/local-only mobile use and optional account
  storage. Defer platform, transfer/sync and notification design to that ticket.
- Update the root roadmap, component READMEs and relevant agent guidance with
  priorities and current-versus-planned behavior. Preserve stable existing IDs,
  completed work records, refocus.md and research; remove only stale guidance.

## Reuse

- Existing raw Psycopg SQL, OTP/session auth, meter/ledger APIs, reminder runner,
  SMTP/delivery claims, roadmap 55/65/66/68 and current MUI layout.

## Verify

- Check consistent IDs, dependencies, requirements, links and whitespace.
- Confirm no code, SQL, config, .env, data, service or historical record changes.
- Record planning results and unresolved implementation decisions in changes.md.

## Out of scope

- Executing the new tickets, resets/migrations/seeding, real emails, new services,
  forecast changes/adoption, UI redesign, mobile implementation, siblings,
  commits and pushes. Each implementation needs its own approved prompt.
