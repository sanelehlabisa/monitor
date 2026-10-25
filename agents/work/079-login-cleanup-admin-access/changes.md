# Task 079 results

Completed 24 October 2026 at the user's direct request; no commit or push.

## Changes and cause

- Removed the unnecessary tagline Chip and its unused import from
  software/frontend/src/routes/login/LoginPage.tsx. Login behavior is unchanged.
- Production deliberately installs schema only in its own volume. Development's
  admin/demo seed is not applied there. The approved existing account was therefore
  a regular user after signup, which correctly hid the admin All tab.
- Explicitly changed only that existing approved account's type to admin using a
  parameterized transaction, locked account lookup, expected-role guard and bounded
  statement/lock timeouts. No account creation, seed replay or schema change.
- Corrected the database README's retired operator-guide link and documented
  separate databases and browser reload/My/All behavior. Updated current context.

## Reuse and checks

- Reused DB-owned roles, AuthenticatedUser/meter_access_scope and list_meters.
  Independent read-only code review found no authorization defect.
- After commit, a new read-only DB connection confirmed admin. Existing scope
  functions returned both production meters for All and one membership for My.
  Other accounts' roles and all nine domain-table row counts were unchanged.
- Frontend Docker build passed TypeScript and Vite; existing bundle-size advisory
  remains. All 22 existing App UI checks passed in an offline disposable container,
  including login flow and admin My/All. No new tests or dependencies.
- Source search confirms the removed tagline is absent. Whitespace check passed.
- Temporary labelled test container and image were removed. Initial cleanup's
  PowerShell Go-template quoting failed before mutation; JSON label verification
  succeeded on retry. Production services remained healthy; none were recreated
  or restarted. No real mail, sessions, fixture meters or ledger rows were added.

## Handoff

Reload the browser to load the account's current role, then select All. Production
and development meters remain in separate databases. Fresh production setup stays
schema-only with explicit admin assignment, never automatic role re-promotion.

Production still serves the prior frontend build. From software/, apply the UI edit:

```sh
docker compose -f prod.docker-compose.yaml up -d --build --no-deps frontend
```

Prior uncommitted tasks, actual environment, data and recovery/research files remain.
