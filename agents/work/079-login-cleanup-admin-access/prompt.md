# Task 079: Login cleanup and production admin access

## Aim

Remove unnecessary login copy and restore the user's expected production admin access.

## Clarifications

- The user requested this minor fix directly: remove the software-only tagline
  and investigate/fix their production admin access. Their previously approved
  admin email remains hlabisasanele730@gmail.com; no new role policy is needed.
- Read-only inspection confirms that account exists as user in production.
  Production installs schema only; the admin/example seed belongs to development.
  Both Compose projects use separate databases. Existing permission code is correct.

## Change

- Remove the login tagline Chip and unused import.
- Explicitly promote only the existing approved production account from user to
  admin in one transaction. Do not create accounts or replay seeds.
- Correct the stale database operator-guide link and clarify current context.

## Reuse

Existing DB user/admin roles, per-request authentication and admin My/All scope.

## Verify

Build the frontend and run its existing UI checks. Verify the target DB role and
  existing meter scope with read-only queries; preserve all other rows and roles.
Record actual checks and results in changes.md.

## Out of scope

Fresh-install seed policy changes, database reset/migration, new authentication
logic, UI redesign, service restart/recreation, real email, commits and pushes.
