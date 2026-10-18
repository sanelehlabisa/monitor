# Task 063: Shared-meter backend

## Aim

Implement simple shared-meter backend access, verified in isolation before live activation.

## Clarifications

- Sharing creates a missing regular user by email and links their ID through
  user_meters. Preserve existing roles; no invitations or automatic promotions.
- Any current member or admin may manage or permanently delete the meter/history.
  Leaving removes membership only; OTP remains required to sign in.
- Backend only: sharing UI and live database activation need separate approval.

## Change

- Create meters/creator memberships atomically. Add member list/share/remove
  endpoints at /api/meters/{meter_id}/members: GET, POST {email},
  DELETE /{user_id}. No global account directory or account-existence flags.
- Authorize before provisioning; reuse email validation and make user/membership
  inserts idempotent, race-safe and transactional. Never overwrite roles or
  create sessions; roll back newly created users when sharing fails.
- Apply membership/admin authorization consistently across every meter, ledger,
  dashboard, reminder and member endpoint. Search names/member emails in SQL,
  returning each accessible meter once. Retain creator response fields as
  compatibility metadata, not access authority.
- Lock the meter, then recheck access separately before membership changes or
  deletion. Reject last-member removal, including concurrent/admin requests.
- Restrict fresh creator/member-user FK deletion to protect shared data; preserve
  explicit whole-meter cascades. No account-delete API, transfer flow or triggers.
  Keep reviewed backfill/FK upgrade SQL under this work directory; rehearse only
  on an isolated current-data copy after verified backup/restore. Preserve all
  records, roles, sequences and both histories; keep database/ at three files.
- Keep legacy opt-in owner reminders until 69.7, but skip removed creators,
  tolerate removal during a run and recheck eligibility before sending.
- Update current docs/context and changes.md. The expected 350-500 implementation
  lines need an exception for coherent authorization/safety, not new architecture.

## Reuse

- Existing raw SQL, memberships, DB roles, email validation/OTP/cookies, scoped
  repositories, forecast boundary, reminder runner and isolated verification.

## Verify

- Confirm source apps remain stopped before edits; ask if unexpectedly running.
- Run isolated backend checks for provisioning/OTP, preserved roles, duplicate/
  concurrent signup/sharing, rollback and unauthorized requests creating nothing.
- Check every protected path, immediate removal, scoped search, concurrent
  last-member protection, permanent deletion and removed-creator reminders.
- Verify fresh/copy schemas and complete copy data preservation, restrictive
  deletion, API changes, links and whitespace; clean only owned test resources.

## Out of scope

- Live DB writes/upgrades/resets, source-service actions, real email, sharing UI,
  mobile/invitations, new roles/dependencies/frameworks, model changes, 69.6/69.7
  delivery redesign, research/backup deletion, siblings, commits or pushes.
