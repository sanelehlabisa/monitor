# Task 049: Sign-out icon

## Aim

Make the existing red Sign out button recognisable with a distinct logout icon.

## Clarifications

- Keep the icon beside Sign out text on all screens: Yes.
- Retain the red button and email; narrow-screen emails may truncate more: Yes.

## Change

- Add the existing MUI Logout icon to the navigation button, distinct from Back.
- Keep compact spacing, the email, centred branding, logout handler and busy guard.
- Update the focused rendering check, frontend README, context and changes.md.

## Reuse

- Existing MUI icons/button and Navigation component; no new dependencies.

## Verify

- Frontend checks, TypeScript/Vite build and git diff --check.
- Focused phone/tablet/desktop check for icon/text visibility, no overlap and
  unchanged direct sign out/pending behaviour, using mocked data only.

## Out of scope

- Other layout changes, account menus, backend/data, forecasting, artwork,
  dependencies, sibling repositories, commits and pushes.
