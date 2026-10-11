# Task 038: Navigation and linkable meter demo

## Aim

Make the meter planning flow clearer and ready for admin testing (Ticket 61).

## Clarifications

- Use a far-right signed-in email/avatar menu with a black Sign out action and
  a distinct logout icon; move Back to meters into the navigation.
- Meter pages need their ID in the URL, details first, then a spacious planning
  card based on the supplied example. Keep forms/history/settings on demand.
- The user chose a separate demo user with a couple of populated meters, visible
  to the existing administrator through All meters. Do not invent real forecasts.

## Change

- Add responsive navigation with the existing brand, Back action and right-aligned
  account menu. Keep the admin indicator; use different Back and Sign out icons.
- Use `/meters/<id>` with browser history, direct links/reload and Back/Forward.
  Restore the requested meter after login; handle invalid/inaccessible links
  without exposing another user's data. No routing dependency.
- Put meter name/owner in a compact details section above the wider planning
  card; preserve the three estimates, actual reading, timestamps and entry actions.
- Through existing local OTP/Mailpit and meter/ledger APIs, create a dedicated
  `monitor-demo@example.test` account with Demo Home and Demo Shop. Populate valid
  synthetic balance/top-up histories with different usage rates, producing real
  backend forecasts. Retain these demo records for the user's testing; clearly
  identify them by demo names/email. Do not overwrite existing records or create
  duplicates on rerun. Do not add automatic startup seeding or a demo API.
- Update roadmap, context and relevant READMEs; record results in changes.md.
  Allow up to 250 changed implementation lines for navigation, URL/state handling
  and layout across existing components; this exception keeps one coherent flow
  reviewable without a router or backend rewrite. Preserve uncommitted Task 037.

## Reuse

- Existing MUI components/icons, auth/logout, meter selection and guarded dashboard
  loader, admin All meters/search, ledger APIs and UTC/local date helpers.
- Existing live browser checks and Mailpit capture; forecasts remain behind the
  existing deterministic model and raw-SQL repositories.

## Verify

- Check account menu/logout and distinct Back action on desktop and narrow phones.
- Check meter URLs, direct reload, login return, browser Back/Forward, invalid or
  inaccessible IDs, and stale dashboard responses after leaving a meter.
- Verify both retained demo meters have numeric forecasts, UTC records and admin
  visibility/manage access; another regular user cannot access them. Leave empty
  real meters at Not enough data. Remove only disposable verification fixtures.
- Run relevant frontend checks, production asset build and diff check; record
  actual results and demo access instructions without credentials.

## Out of scope

- Forecast-policy/model or backend permission/schema changes, new dependencies,
  automatic seeding, reminders, new logo, VPS deployment, tariffs/payments,
  hardware/OCR/ML. No commit or push without a new request.
