# Task 093: Clean login entry

## Outcome
Home has one Log in button. `/login` offers email login or guest use.

## Questions and answers
The user explicitly requested this correction to Task 092. No unclear requirements.
Remove unnecessary account-saving/storage copy; keep actual failure recovery.

## Scope and reuse
Reuse App route state, LoginPage, Navigation and the existing guest workspace.
Keep email/code behavior and protected account links. Remove the routine guest
storage paragraph/row. This request authorizes the small UI correction.

## Verification
Frontend build, existing checks and isolated browser entry/navigation checks.
Verify guest records survive navigation and mobile layout stays compact.

## Exclusions
Account import, session-policy changes, database, dependencies, live services,
deployment, commits and pushes.
