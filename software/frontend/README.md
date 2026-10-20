# Frontend

React, Vite and Material UI application with passwordless email login, meter
management and manual kWh history. It restores cookie sessions through
`/api/me`, supports email/code/resend/logout, and lets a signed-in user add,
list, select, rename and delete nickname-only software meters.

The following describes the current UI. Task 059 makes stored DB roles active;
Task 063 implements the shared backend; Task 064 applied its safe DB transition.
After the initial health timeout/diagnostic, the user started the full stack.
Read-only checks passed for served UI/deep links, transformed main/App modules,
branding assets and signed-out API denial through the frontend proxy. Services
remain running; live browser/login/write verification is still outstanding.
Task 065 adds minimal sharing and membership-aware My; Task 066 adds calendar-month planning.

Regular users receive their accessible meter memberships from the backend.
Users whose stored type is `admin` can see every meter's creator email and the same
select/rename/confirmed-delete controls for all meters. Task 039 hides the nav
role badge without changing administrator access. New
meter creation remains intentionally name-only and always belongs to the signed-
in user.

Administrators default to `My`: meters they currently belong to, including shared-in
meters but excluding those they left. `All` shows every system meter with Created by
labels and the same controls. Both views are server-scoped; switching views does
not change membership or backend authority.

Task 047 shows Search/Clear only when the selected view has more than 10
unfiltered meters, or a query/filter is active. It sits between Meters and
My/All on tablet/desktop and on its own header row below 600px; never on details.
Erasing a draft does not discard the applied filter or disable its Clear action.
Zero/one-result searches keep the field visible; a successful full reload clears
filtering. My/All requests the selected server scope, and create/delete keep the
unfiltered count current. Account changes reset counts/query and ignore old replies.

Search calls `GET /api/meters?q=...&mine=true` for My; admin All omits `mine`.
Regular users remain limited to current memberships regardless of that flag.
The backend matches names/current member emails. There is no duplicate
client-side keyword matching or pagination. Visible meter rows are numbered
1, 2, 3... in their current order, restarting for each search/view; these are
display ordinals, not persisted meter identifiers. Create remains unnumbered.

Development uses polling to watch bind-mounted sources because Docker Desktop
can miss native file-change events. When dependencies change, refresh the named
frontend dependency volume and restart the frontend as described in the software
README; rebuilding an image alone does not update an existing dependency volume.

Run checks from this directory with:

```powershell
npm test
npm run build
```

## Source layout (Task 062)

`App.tsx` keeps session state, manual URL/history handling and coordinated
meter/ledger requests, including the existing stale-response guards. Screens
and their existing components are grouped without a new routing dependency:

```text
src/
  App.tsx, main.tsx
  routes/login/LoginPage.tsx
  routes/meters/MetersPage.tsx, MeterDetailsPage.tsx, meterRoute.ts
  routes/meters/components/MeterSection.tsx, MeterSearch.tsx
  routes/meters/components/ForecastPanel.tsx, LedgerPanel.tsx
  routes/meters/components/SharingPanel.tsx
  components/Navigation.tsx
  lib/api.ts, dateTime.ts, theme.ts
```

API/date/route-helper tests live beside those helpers; `App.test.tsx` retains the
existing screen assertions. Login is still the unauthenticated view at the
requested URL, not a new `/login` route. Page keys, form resets, appearance and
request behavior are unchanged. The old mixed screen files have no re-export
shims; their committed originals remain recoverable from Git history.

## Docker targets

`development` retains Vite on port 5173 and bind-mount reload. The default
`production` target builds with the existing npm lockfile and copies only `dist/`
into `nginx:1.30.5-alpine3.24`; Node/npm and application source are not copied into
the serving stage. Local `.env*` files are excluded from the build context.

Nginx listens on port 80. It forwards `/api` and `/api/...` to `backend:8000`
without stripping the API path, while other application routes fall back to
`index.html`. Missing `/assets/...` files return 404 rather than SPA HTML. A
backend network alias/service must exist before Nginx starts. HTTPS/public proxy
configuration is deferred; production cookie login requires HTTPS. Build
commands and completed image verification are recorded in the software README.

## Navigation and meter links

Task 048 keeps Back on the left when a meter is open and replaces the former
account icon/dropdown with a direct red Sign out button on the far right.
The signed-in email sits beside it with a 4px gap on phones, tablets and desktop;
it truncates rather than displacing the button or branding, with the full email
retained as text/title. Sign out reuses the existing handler and pending guard.
Task 049 adds the MUI Logout icon beside Sign out on every screen, distinct from
the Back arrow. A compact icon gap and narrower phone padding preserve space
for the email; longer emails may truncate further. The red button and label stay.
Task 044's combined branding stays: a 48px logo above the Monitor name in the
centre, with both navigation controls vertically centred against that block.
Equal flexible side columns keep branding centred even without Back.
Login/session loading retain centred stacked branding without navigation controls.
The company artwork stays in the footer; the old title/Admin badge remain absent.

Selecting a meter uses `/meters/<uuid>`. Direct links and reload restore the
authorised meter, including after email login; browser Back/Forward and the Back
button update the workspace without a routing dependency. Malformed, missing
or inaccessible meter links show recovery guidance without exposing another
user's records. Task 041 uses `/meters` for the list; `/` and `/meters/` remain
compatible entry links and canonicalise after sign-in. Back and logout return to
`/meters`. Failed opens
can be retried, and leaving a meter invalidates older dashboard responses.

The signed-in container is wider. Task 040 places compact Name/Owner key-value
rows above the full-width three-estimate planning summary (Task 065 relabels Owner
as Created by, historical metadata only). Task 041 starts Name
read-only: pencil enables/focuses editing, then becomes Save. Save/Enter persists;
Escape cancels; success returns to read-only and errors retain the draft. Owner
is always read-only. The same edit/save behaviour applies to list rows.
The bottom Meter settings section is removed; record actions and collapsed
forms/history are unchanged.

Every accessible meter-list row has separate pencil/trash actions next to the
meter-opening button. Pencil opens an inline name editor; Save/Enter persists,
Escape cancels. Trash confirms the named meter and warns that its balance/top-up
records will also be deleted. Actions do not open the meter or nest buttons.
Rename failures retain the draft for retry; conflicting controls are disabled
while saving, without hiding the row. A rename under search refreshes the server
query rather than introducing client-side keyword matching. Administrators have
the same actions for every meter in All meters. Task 063 updates backend access
to memberships without adding sharing controls to this UI.

Task 039 centralises typography in the existing MUI theme: one Arial/sans-serif
font stack, 16px body/labels/buttons and 20–22px headings/forecast values at the
default browser text size. Task 041 reduces the scale to 14px body/labels/buttons,
18px headings and 20px forecast values, with smaller fields/button padding.
Button/tab labels no longer force uppercase; stored name casing is untouched.
Rem units retain text scaling. Task 040 replaces the
earlier name/owner heading with aligned keys and values, including on phones.

Task 041 introduced the signed-in section header, which Task 043 changes from
black to the shared brand blue, with white text and rounded
top corners: `Meters` for the list and `Meter <UUID>` for details. Admin-only
My/All tabs sit at the list header's far right; the active tab is white with
blue text and joins the content below. Filters are not shown for one meter.
The full detail ID can wrap on narrow phones rather than overflow.
Task 046 supersedes the filled header/card styling with open sections and
underlined admin tabs, retaining those titles and permissions.

Search has magnifying-glass and clear-cross actions inside the input's right
edge, with accessible labels/tooltips. Enter also submits; clear reloads the
server list. The first list row contains only a name input plus an Add icon,
including empty/search states. Creation still belongs to the signed-in user;
search matching remains backend-driven, with no new API or client-side filter.

### Small visual polish (Task 045)

The shared MUI theme now uses Segoe UI/system sans-serif fallbacks without font
downloads. The compact scale stays 14px body/buttons, 18px headings and 20px
forecast values, with consistent heading/button weights and tabular estimate
digits. Existing wording, controls and content order are unchanged.

Primary blue #005aae, teal #007782 and light-blue #e2f0ff hover/focus remain.
Task 045 initially added tinted cards and a forecast gradient; Task 046 replaces
those choices with the open layout below while retaining its compact typography,
10px input corners and explicit button/icon-button keyboard-focus outlines.
Stacked branding, routes, forms, calculations and factual/estimated labels remain.
This visual pass does not complete the wider Ticket 65 usability review.

### Open phone/tablet layout (Task 046)

Login and the workspace are plain sections on a white page, not enclosing cards.
Slim blue headings and divider lines replace filled title bars. Admin-only My/All
tabs retain their existing ARIA relationships and use the standard blue underline.
Meter details, name-only creation and list rows are flat and divided; inputs,
edit/delete icons and hover/focus feedback stay visible.

The forecast is an open section with muted labels, blue balance/days and a teal
monthly purchase value. It has no coloured background, rounded box or shadow.
At widths below 600px the figures stack; 600–899px shows balance/days together
and the monthly recommendation underneath; 900px and wider shows three columns.
Latest actual reading/time and calculation time remain separate below. The two
record actions stay prominent, forms open on demand, and History starts collapsed
below a divider. Existing navigation, handlers, record order and math are unchanged.

## Mobile flow

1. Enter email and verify the one-time code.
2. Create or select a meter/property by nickname.
3. Review the prominent planning estimate and its latest factual reading.
4. Select Record balance or Record top-up to show its form. Save closes the form;
   Cancel closes it without writing. Date/time defaults to the browser's local time.
   Expand History to use the record tabs for correction/deletion; it starts
   closed. Use the pencil beside Name above the estimates, or pencil/trash
   on its list row to rename/delete it.
5. Use Refresh to request current estimates without adding a record or reopening
   the meter. Estimates are a snapshot at the displayed local calculation time.

The primary entry actions must take only a few seconds on a phone. Do not require
a municipal meter number, tariff, Rand amount, image or device setup. Show the
last actual reading time beside estimated balance, daily usage, remaining days,
predicted run-out, next monthly top-up date and actual-month recommended kWh.

Use "Not enough data" when the backend cannot support a forecast. Make correction
and deletion behavior explicit; never hide inconsistent history behind a smooth
chart.

Future UI may take inspiration from the sibling Switch dashboard's compact cards,
clear primary actions and mobile sizing, but Monitor stays a native React/Material
UI implementation. Task 014 uses those principles and a local copy of the
approved circular Roventics robot logo. Development browser requests use relative
`/api` URLs through Vite's proxy to the backend; cookies never enter browser
storage or page text.

The signed-in home loads real nickname-only software meter profiles from the
cookie-authenticated API. Creation asks only for a name. Selecting a meter loads
its actual balances and purchased top-ups, shows the latest factual balance,
and provides compact create/edit/confirmed-delete controls for both record
types. Each tab under the collapsed History section shows its own newest-first
factual history; the entry forms are shown only after choosing a record action.

Task 037 simplifies the selected meter dashboard around one planning summary:
estimated balance and days remaining, a smaller predicted run-out date below
remaining days, and a monthly purchase recommendation. Task 066 shows the next
monthly top-up date separately in UTC and uses that full calendar month's days
minus current estimated balance, not a future-balance projection, Rand cost or
different learned model. Latest actual balance/observation time
and the estimate timestamp remain visible; daily usage/interval assumptions sit
inside collapsed Calculation details. Two large icon buttons reveal only the
matching entry form. The header is compact and retains the meter name/owner.

The dashboard reloads after every ledger change. Task 035 adds an icon-labelled
Refresh action, which Task 037 moves below the primary content. It
uses the same dashboard loader as meter opening and successful ledger changes;
there is no automatic API polling. Task 066 checks the calendar locally with
bounded timers and focus/visibility events, fetching once when the UTC planning
cycle expires. It defers conflicting work and preserves manual error recovery.
Refresh is disabled while loading or saving.
Failed reads hide estimates and show `Estimates unavailable` with retry guidance,
not a permanent spinner. Already-loaded records remain available after failure.
If a write succeeded, its form clears/closes and the message confirms it was saved:
Refresh retries only the read, never the purchase or balance write. Responses
from a meter left, reopened or signed out of cannot overwrite the newer view.

Insufficient or inconsistent history shows an explicit state without invented
numbers; valid zero use has no fake run-out date. The browser does not calculate
forecasts. Backend persistence stays explicit raw SQL through Psycopg, with no
SQLAlchemy, and the replaceable first forecast model is simple math rather than
ML.

Balance and top-up histories are separated into matching tabs inside History.
Record actions select the matching type and open a fresh form; switching a history
tab closes any entry/correction form so its values cannot be applied to another
record type. Datetime
inputs are interpreted in the calling browser's timezone, converted to UTC for
the API/database and rendered locally when returned.

Task 033 removes reminder settings from the frontend to keep the PoC focused.
The backend API and finite runner remain available for existing opt-ins. New
settings still default off, with the existing hardcoded monthly day 1 and
predicted-low-balance lead time of 3 days; the browser makes no reminder calls.

Hardware status, OCR, anomaly, tariff and payment screens are not V1.

## Repeatable local demo

### Retained sample meters (Task 038)

The local development database contains a separate `monitor-demo@example.test`
user with **Demo Home** and **Demo Shop**. These are synthetic demonstration
records, not household readings. They were added once through the existing
OTP/Mailpit and meter/ledger APIs; the application never automatically seeds data.
Setup reuses existing named demo meters without overwriting their histories.

Sign in with your configured administrator account and select the **All** tab.
Find owner `monitor-demo@example.test` in the labelled rows, or use header search
when the view has more than 10 meters. Both profiles can be opened and managed with
the normal admin controls; another regular user cannot read or modify them.
The demo email can also sign in through Mailpit in local development.

At setup on 2026-10-11, Home used 4 kWh/day and displayed approximately 76 kWh,
19 days remaining and an additional 44 kWh for the next 30 days. Shop used
8 kWh/day and displayed approximately 112 kWh, 14 days and an additional
128 kWh. Values change as time passes and Refresh requests a new calculation.
These numbers come from the real backend model, not hardcoded UI values. Real
empty meters still show Not enough data. Both sample profiles are retained for
testing; cleanup below applies only to a new disposable walkthrough meter.

### Disposable manual walkthrough

Use a separate test email and a new meter named `Demo Home`. Get the sign-in code
from local Mailpit at `http://localhost:8025`. Dates below are relative to now;
use the same local clock time for all three records.

| Tab | Record time | kWh |
| --- | --- | --- |
| Balance records | Eleven days ago | 100 |
| Top-up records | Six days ago | 20 |
| Balance records | Yesterday | 80 |

The interval used 40 kWh over ten days: `(100 + 20 - 80) / 10 = 4 kWh/day`.
The summary should show approximately 76 kWh now, 19 days remaining and a
predicted run-out 19 days from now, separate from the next monthly UTC 1st.
Additional purchase is max(0, 4 * target_month_days - 76): 44 kWh for a 30-day
target month, or 48 kWh for 31 days (36/40 kWh for February's 28/29 days).
The latest actual reading stays 80 kWh at yesterday's observation time. Small
differences are expected as time passes; the recommendation subtracts the
estimated kWh currently available, without depleting it to the future 1st.

1. Edit yesterday's balance to 70 kWh. The usage rate should refresh to 5 kWh/day
   without reopening the meter. Restore it to 80 afterward.
2. Edit the top-up to 30 kWh; the rate should become 5 kWh/day. Restore 20 kWh.
3. Delete yesterday's balance and confirm the prompt. One remaining reading
   should show `Not enough data`; add yesterday's 80 kWh reading again.
4. Select Refresh to update the calculation time without creating records.
   Reopen the meter or reload the page; records and the session should persist.
5. In another browser profile, sign in with a second test email. The first
   user's meter must be absent. A configured admin can instead select the `All`
   tab, locate the owner-labelled row (or search by email when available) and
   manage that meter.
6. Delete only the demo meter when finished and sign out.

Input times use the browser's local timezone; the API and database retain the
equivalent UTC instants. This walkthrough verifies the technical flow. A real
household trial is still needed to establish whether manual entry is convenient.

## Usability, identity and future installation

Task 042 created planning requirements only. Task 043 implements identity Ticket
58 below; full usability 65, the Ticket 69 refocus and future installation/local
use under 68 need separately approved implementation. The [root roadmap](../../README.md)
owns execution order.

### Ticket 65: Monitor Usability Review

Review the first-user flow: email login -> name-only meter -> manual balance/
top-up records -> understandable forecast. Keep forms on demand and remove
unnecessary fields/screens, not required ownership or factual timestamps.
Review dashboard wording, mobile layout, keyboard/icon accessibility and empty,
loading, save/error/retry states. A new meter must explain the need for two
valid actual readings without displaying invented numbers.

Make actual reading/time clearly distinct from the estimated current balance,
days/run-out and additional energy to buy. Explain that monthly usage is not the
same as additional purchase: 15 kWh/day means 450 kWh for a 30-day target month; with 300 kWh
already available, the current recommendation is 150 kWh extra.

Acceptance: a concise issue/fix review and first-time desktop/phone walkthrough
covering login, meter creation, records, forecast/unavailable states and recovery.
Reuse the compact MUI workspace and the identity delivered through 58 rather
than redesigning the product.

### Ticket 58: Monitor App Identity

Completed in Task 043 using the user's supplied transparent
public/monitor-logo.png (1254 x 1254), retained unchanged. A 48px logo with the
Monitor name appears above both login and the signed-in workspace, including
session loading. Task 044 stacks the logo above its name and shares one row with
signed-in navigation rather than using separate brand/navigation rows.
Browser title is Monitor; the same PNG is the favicon and
theme-colour metadata matches the primary blue. No PWA or logo regeneration.

The existing MUI theme in lib/theme.ts owns the palette: primary blue #005aae,
accessible teal #007782, a white page and light-blue interaction accents.
Task 046 replaces the earlier cards/filled headers with open blue headings and
blue/teal forecast values; active admin tabs have a blue underline. Top-up and
Refresh use teal; Task 048 makes the company credit black and Sign out red.
Typography stays 14px body/buttons, 18px headings and 20px forecasts; Task 048
removes the former 42px account icon. Task 045 refines the system font, shades,
corners and focus styling as described above. Task 046 changes layout only; the stacked header,
manual forms, history and behaviour remain.

The footer retains the manual-kWh note and the existing 24px Roventics
logo plus black by Roventics text (Task 048). Its https://roventics.com link opens
a new tab with noopener/noreferrer, preserving the current meter. The Monitor identity is
primary; company artwork does not determine the app palette.

Verification includes 31 frontend checks, the TypeScript/Vite production build
and four grouped browser checks across 18 desktop/390px/320px views. Those
browser checks use a disposable built-assets preview with mocked API responses,
not real household data or backend authentication. No real API/DB writes occur.
Task 044's header refinement passes 32 frontend checks, the same asset build and
four focused mocked-browser groups across 16 desktop/600px/390px/320px views:
stacked branding and control alignment, long-email truncation, Back, Sign out,
and Escape/focus restoration. No real backend or database requests are made.

Task 048 passed all 33 frontend checks, the TypeScript/Vite build and two
focused mocked-browser groups with 15 captures at 320/390/600/768/1200px.
These cover direct red Sign out/email alignment, long-email truncation, Back,
keyboard focus, pending controls, logout failure/retry and success, and the
black company credit. The red button's white text measures 4.98:1 contrast.
These are UI checks, not a new backend authentication or household validation.

### Ticket 69.5: Minimal shared-meter UI/API integration (Task 065)

Depends on the database/setup, DB-role and membership/authorization work in
69.1–69.4; see the [database plan](../database/README.md) and
[backend contracts](../backend/README.md). Reuse email-OTP login, secure cookie
sessions, existing meter/ledger APIs and the compact MUI workspace.

Every meter member may manage its balance/top-up records and membership;
global admins retain full access even without membership. Represent membership,
not ownership, in the list/details UI: My means meters the signed-in user
belongs to, and admin All includes every meter. Server-side keyword search must
support meter names and member emails within authorized scope, not only the old
owner email; Task 063 implements this query. The frontend consumes its results.

Surface backend membership/save failures and last-member-removal rejection
without losing drafts or bypassing authorization. Any member/admin may permanently
delete a meter/history. Sharing accepts email, creates missing regular accounts
and links IDs; no invitation or OTP bypass. Keep creator metadata clearly labelled
as Created by rather than treating it as ownership authority.

Sharing starts collapsed below History. Expansion loads members on demand;
email Add provisions/links through the existing backend. Remove and Leave require
confirmation and remove membership only. Permanent meter Delete remains separate.
Failed writes retain the email draft; after a saved change, failed member/list
refresh disables further writes and offers a read-only Retry. Self-leave immediately
clears the workspace and returns to the scoped list, including for admins (who
retain All access). A failed return-list read has its own GET-only Retry.
Meter/account/view generations ignore late sharing replies; successful changes
refresh active server search and its unfiltered scope count.

Acceptance: desktop/phone flows for two members, a non-member and a global admin;
membership/list changes, scoped email search, last-member rejection and recovery.
Keep existing ledger, navigation and stale-response guards. Task 065 verification
uses isolated/mocked data only; it is not live-user or household validation.
All 36 frontend checks and the TypeScript/Vite build pass. Twelve mocked-browser
groups cover sharing, scoped search/counts, last-member/failed-read recovery,
conflicting controls and delayed replies after meter/account changes; six
1200/390/320px captures have no overflow. No real API writes or mail were used.

### Ticket 69.6: Calendar-month planning (Task 066)

The latest user clarification supersedes the former unchanged-30-day plan.
Task 066 uses the strictly-next UTC 1st: once that day starts, target the next
month's 1st. Show this calendar date separately from Predicted run-out, never as
a promise the meter will last until then. Preserve the existing open layout.

Use backend rate × actual target-month days minus CURRENT estimated balance,
floored at zero. Compute duration from the target 1st to the following 1st using
UTC datetimes, not a fixed 30. Example: 15 kWh/day, 300 kWh available and a 28-day
February gives 120 kWh extra. Do not project/deplete balance to February 1 or
introduce another learned model. Preserve honest unavailable and zero-use states.

The API uses recommended_monthly_top_up_kwh, planning_at and planning_days,
with no old 30_days field. Display its date in UTC so a browser cannot shift the 1st to
the previous day; factual ledger/run-out display keeps its existing local format.
Task 067 removes only the visible " (UTC)" suffix from this date label; the UTC
calendar formatter and all calculation/rollover rules stay unchanged.
Its 43 frontend checks and TypeScript/Vite build pass, including the UTC-versus-
western-date helper checks and the suffix-absence assertion.
Recalculate after existing Refresh/ledger actions; an open view performs a
guarded read-only refresh at month rollover or after resuming an outdated view.

The [backend plan](../backend/README.md) owns 69.7 automatic monthly mail to each
meter's members at 09:00 UTC on month-end, persisted per-recipient status and
backend-startup catch-up. No user selectors/settings are added. Task 066 changes
existing message wording only; it does not activate or implement the scheduler.

Task 069 adds only a small monthly-schedule policy note inside collapsed Sharing.
No reminder controls, handlers or dashboard layout change. The user confirmed
monthly-only automation; shared low-balance warnings remain deferred. All 43
frontend checks and TypeScript/Vite build pass. Local emails go to Mailpit only;
production/external delivery remains separately approved deployment work.

Acceptance: desktop/phone target-date/amount wording, first-day advancement,
28/29/30/31-day and year/UTC boundaries, unavailable/zero-use states, unchanged
rate/run-out, API/email agreement and stale-response-safe read-only rollover.
Failed automatic reads use existing manual Refresh recovery; no ledger write is
replayed. The clock check cancels on navigation/account changes and suppresses
duplicate timer/focus/visibility requests for an expired workspace/cycle.
All 43 frontend checks, TypeScript/Vite build and 11 mocked-browser groups pass.
Four desktop/390/320px captures cover calendar/unavailable layouts; western
timezone, month rollover/resume, read-only recovery and stale responses are
verified without real API requests. Task-owned verification resources are cleaned.

### Ticket 68: Future installation and guest/local-only use

After personal/external web-usage evidence (56/67), scope a minimal installable
experience. Guest/local-only mobile use needs no login and keeps records in local
device storage; account storage and shared meters require login and server authorization.
This is a future mode, not permission to bypass the current app's authentication
or store session credentials in local storage.

Choose the platform and persistence approach in that ticket; no PWA framework,
native framework, store release or new service is committed here. Decide local
data durability/loss, guest-to-account transfer, duplicates/conflict handling,
multi-device synchronization, connectivity/stale-estimate behaviour and
notifications before implementation. Never present a stale estimate as fresh.
Account/sharing integration depends on the relevant Ticket 69 contracts above.

Acceptance: an approved platform/storage and transfer/conflict design, followed by
a focused guest-local versus authenticated-account flow and install/open check.
No caching, sync, mobile implementation or notification expansion is added now.
