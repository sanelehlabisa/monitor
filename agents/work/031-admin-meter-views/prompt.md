# Task 031: Admin meter views

## Aim

Make it quick for an administrator to test their own meter profiles while still
retaining full access to every meter profile in the system.

## Clarifications

- Question: What behavior already exists? Answer: Users create and manage only
  their own meters; admins create meters owned by their admin account and may
  fully manage every user's meter.
- Question: How should the admin list be separated? Answer: Add compact `My
  meters` and `All meters` views, defaulting to `My meters`; `All meters`
  includes every profile and continues to identify its owner.
- Question: Who owns a meter created by an admin? Answer: Keep the current safe
  behavior: it belongs to the signed-in admin, with no create-on-behalf flow.
- Question: Does regular-user behavior change? Answer: No.

## Change

- Add a small Material UI view selector for administrators only.
- Filter the existing loaded meter list by normalized owner email for `My
  meters`; leave `All meters` unfiltered and owner-labelled.
- Keep the name-only add form visible and make newly created admin meters appear
  immediately in both applicable views.
- Give each view a clear empty state without implying physical hardware.
- Update focused frontend coverage and nearby documentation.

## Reuse

- Reuse the existing meter list, owner email returned by the API, selected-meter
  workspace, add/select/manage actions and Material UI components.

## Verify

- Run frontend tests and the production build.
- Exercise an administrator through the development frontend: create a meter,
  see it under `My meters`, switch to `All meters`, and open another owner's
  meter with full management controls.
- Run `git diff --check`.

## Out of scope

- Backend or database changes, creating meters for another user, roles beyond
  the configured admin email list, physical devices, hardware provisioning,
  sharing, tariffs, payments, OCR and ML.
