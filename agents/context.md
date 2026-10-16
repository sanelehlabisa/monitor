# Repository Context

Monitor is a free, software-only electricity planning application for
prepaid households. It helps users understand how much electricity to add and
when through manual kWh records and simple, transparent forecasts.

## Active V1

A user authenticates by email OTP, creates one or more named meter/property
profiles, and records two kinds of events:

- actual remaining balance in kWh at an observed date/time; and
- manually purchased top-up energy in kWh at a purchase date/time.

Dates default to now but remain editable. A municipal meter identifier is not
required. Each meter belongs to its user in V1, and every API/query must enforce
that ownership. Sharing and multi-user meter access require later evidence.

V1 does not accept Rand amounts, use tariffs or execute purchases. "Top-up"
means recording electricity already bought. Users may opt into monthly planning
email or a predicted-low-balance email when a valid forecast exists.

## Forecast contract

Between two valid actual balance readings:

```text
consumption_kwh = previous_balance_kwh
                  + top_ups_kwh_during_period
                  - current_balance_kwh

daily_usage_kwh = consumption_kwh / elapsed_days
```

Use deterministic calculations and show their assumptions. At least two actual
balance readings with positive elapsed time are required before calculating a
usage rate. Account for top-ups inside the interval. Reject or clearly surface
impossible negative consumption, duplicate/reordered times and inconsistent
entries. Never turn insufficient data into a confident prediction.

Estimated current balance, remaining days, likely run-out/next-top-up date and
a 30-day kWh recommendation must be labeled as estimates. Always show the latest
actual reading and its observation time beside forecast output.

## Active technology

- `software/backend/`: FastAPI REST service and pure forecasting/domain logic.
- `software/database/`: PostgreSQL with explicit versioned SQL through Psycopg;
  no ORM.
- `software/frontend/`: React, Vite and Material UI, designed mobile-first.
- `software/ocr/`: deferred research only, not an active dependency.
- `hardware/`: deferred research only, not an active V1 dependency.

Development runs PostgreSQL, Mailpit, backend and frontend through
`software/dev.docker-compose.yaml`. No production/cloud infrastructure should be
added without an approved ticket.

## Authentication

Tasks 005-006 are historical records of the superseded Keycloak baseline. Task
007 removed that integration. Task 010 allows open email signup and implements
normalized user/OTP storage plus HMAC-only challenge policy. Task 011 delivers
those codes through an SMTP abstraction and isolated Mailpit development
capture. Task 012 adds digest-only, fixed 30-day session storage and policy. A
user is created only after successful verification. Task 013 exposes the human
authentication routes and transports opaque sessions in secure HTTP-only
cookies. Generic request responses avoid account enumeration, and neither email
nor an OTP is an API token.

Device UUIDs, device credentials and provisioning are not V1 requirements.
They remain future research if automated meter capture is later justified.

## Work history and current direction

- Tasks 001-004 created the repository, three-service Docker stack, FastAPI
  baseline and direct-Psycopg migration system.
- Tasks 005-006 implemented the now-superseded Keycloak path.
- Task 007 removed Keycloak and retained the Material UI foundation.
- Task 008 changes active planning from camera/OCR collection to manual kWh
  entries, forecasts and reminders. It does not implement those features.
- Task 009 aligns the inactive Material UI shell with that product direction.
- Task 010 adds open-signup user/OTP storage and policy without HTTP or delivery.
- Task 011 adds SMTP OTP delivery and Mailpit capture without an HTTP surface.
- Task 012 adds opaque multi-device session storage and policy without HTTP.
- Task 013 completes the human auth API and HTTP-only cookie transport.
- Task 014 adds the session-aware Material UI login flow and branded meter-list
  empty state.
- Task 015 adds raw-SQL nickname-only meter persistence and owner-scoped CRUD.
- Task 016 exposes authenticated meter CRUD. Regular users are owner-scoped;
  emails configured in `MONITOR_ADMIN_EMAILS` may manage all existing meters.
- Task 017 connects the Material UI home to real meter list/create/select APIs
  and keeps a newly selected meter at `Not enough data` until ledger work lands.
- Task 018 completes Ticket 49 with rename/delete controls and an administrator
  view that identifies owners and manages all meters. Regular-user isolation is
  unchanged.
- Task 019 adds raw-SQL actual balance observations with non-negative three-
  decimal kWh, unique per-meter occurrence times and scoped correction/deletion.
- Task 020 adds raw-SQL purchased top-up events with positive three-decimal kWh,
  repeated occurrence times and the same scoped correction/deletion behavior.
- Task 021 exposes nested authenticated balance/top-up CRUD, rejects future or
  timezone-naive events and applies the established user/admin meter scope.
- Task 022 completes the balance/top-up delivery with mobile-first Material UI
  entry, correction, deletion, latest-actual and combined-history states.
- Tasks 023-024 complete Ticket 52 behind one replaceable
  `run_forecast_model` function. Its first implementation is deterministic,
  time-weighted math with explicit unavailable states and no hidden buffer.
- Task 025 exposes a freshly calculated, authorised meter dashboard containing
  latest actual data, separate ledgers, combined factual history and forecasts.
- Task 026 completes Ticket 54 with responsive Material UI estimate cards and
  automatic dashboard refresh after every successful ledger change.
- Task 027 adds opt-in raw-SQL reminder preferences per meter, including monthly
  day, predicted-low-balance lead days and browser-supplied IANA timezone.
- Task 028 adds durable reminder delivery claims and a finite runner that sends
  owner-only monthly/low-balance email through the existing SMTP boundary.
- Task 029 exposes authenticated owner/admin reminder preference reads and saves
  without exposing or triggering the delivery runner.
- Task 030 adds per-meter Material UI reminder controls with disabled defaults,
  browser timezone capture and clear forecast limitations.
- Task 031 separates the administrator workspace into `My meters` and `All
  meters`, keeping admin-created profiles owned by the admin while retaining
  full management access to every user's profile.
- Task 032 adds owner-scoped raw-SQL meter keyword search by profile name or
  owner email and a minimal frontend Search/Clear form that consumes it.
- Task 033 widens and reorganizes the selected-meter UI around a prominent
  planning summary, a meter/owner header and separate balance/top-up tabs. It
  removes reminder configuration and requests from the frontend while leaving
  the reminder backend, disabled defaults and existing opt-ins unchanged.
- Task 034 verifies the live browser sign-in, meter/ledger/forecast flow, UTC/local
  timestamps, user isolation and admin access. It enables Vite polling after
  finding stale Docker-served modules, refreshes the existing frontend dependency
  volume and documents a repeatable local demo. Technical checks passed; Ticket
  56 remains open for real household usability feedback. Task 042's current
  release order below supersedes the earlier household-before-deployment gate.
- Task 035 completes Ticket 59 with an icon-labelled manual Refresh action and
  one shared dashboard loader. Failed initial/manual/post-save reads withhold
  estimates, retain available records and provide retry guidance. Reads never
  repeat saved writes; navigation/sign-out invalidate older dashboard responses.
  No automatic refresh, dependency, backend or forecast-model change was added.

Household validation and deployment remain later steps. Task 043 delivers the
supplied Monitor identity; the next priority remains usability Ticket 65.

Task 036 is complete: production
targets use a pinned Nginx frontend runtime and non-root Uvicorn without reload;
development Compose explicitly selects the retained development targets. Local
env files are excluded and production credentials remain runtime inputs. Docker
recovered after the earlier approved restart/WSL startup timeout. Both production
and development images built successfully; disposable checks passed for health,
static assets, SPA fallback, API proxying/errors, secure cookie headers and
production-secret refusal. Task containers/network were removed; no stored data
or existing volumes were removed. The existing four development services are
healthy. This is preparation under Ticket 57, not authorisation to deploy, change
DNS or start the remaining deployment work. Household validation remains open.

The user now wants a simpler dashboard based on their supplied example: estimated
balance, days remaining and monthly purchase kWh first, followed by Record balance
and Record top-up buttons. They confirmed forms/history/settings should appear
only when needed, with the run-out date beneath days remaining and a labelled
latest actual reading. Task 037 (Ticket 60) is approved and implemented: the
planning card shows those three headline values, record buttons open only their
matching forms, and history/settings/calculation details start closed. Save or
Cancel closes the entry form; retry/error states remain visible independently of
collapsed sections. The header is compact and Refresh is a smaller action below
the primary content. Desktop and 320px/390px browser checks, the 22 frontend checks
and the asset build passed. Synthetic fixtures were cleaned up. Forecast math
is unchanged. Earlier prospective
037-038 deployment numbering was not allocated work; the remaining deployment
scope stays deferred under Ticket 57 and needs separate future tasks.

Task 038 (Ticket 61) is complete: right-aligned account email/avatar navigation
with a black, distinct Logout action; Back to meters in navigation; meter-ID
URLs supporting reload, login return and browser Back/Forward; and a wider
details/planning layout. Invalid/inaccessible links recover without exposing
foreign records, and older dashboard responses remain guarded. A separate
`monitor-demo@example.test` user owns retained Demo Home and Demo Shop profiles
created through local OTP/Mailpit and existing APIs. Their synthetic histories
produce 4 and 8 kWh/day respectively through the real model; admins can find
both through All meters/email search. Setup rerun preserved histories without
duplicates. Desktop/320px/390px live checks, 30 frontend checks and the production
asset build passed. Only disposable verification users/records, captured emails
and the temporary admin session were removed. Forecast policy, permissions,
backend SQL and real household data are unchanged. See the frontend README for
demo access instructions.

Task 039 (Ticket 62) is complete: navigation has Back on the left and email plus
a 28px account icon on the right, with no logo, Roventics Monitor name or Admin
badge. The logo asset is retained. The MUI theme uses one Arial/sans-serif font
stack with 16px body/labels/buttons and 20–22px headings/forecast values. Meter
name/owner are vertically centred on desktop and stack left-aligned on phones.
Desktop/320px/390px live checks, 30 frontend checks and the asset build passed.
Both demo histories were compared before/after and remain unchanged; no ledger
writes were performed. Routes, admin permissions, model and backend are unchanged.
Temporary verification auth fixtures were cleaned up.

Task 040 (Ticket 63) is complete: the account icon is 42px (1.5 times Task 039's
28px). The selected-meter header now has aligned Name/Owner key-value rows,
an editable name input and a pencil-only save action; Enter also saves. Bottom
Meter settings is removed. Each accessible list row has separate pencil/trash
actions: inline rename with pencil/Enter save and Escape cancellation, plus
confirmed deletion warning about associated records. Shared existing API handlers
preserve owner/admin scope and re-query server search after renaming. Pending
saves retain the row and disable conflicting actions. Desktop/320px/390px live
checks, owner/admin actions, failure recovery, 30 frontend checks and the asset
build passed. Both demo histories are unchanged; no ledger writes or reminder
calls occurred. Only disposable verification fixtures were removed. Backend,
forecast model, routes, dependencies and real data are unchanged.

Task 041 (Ticket 64) is complete: the signed-in card has a black, white-text
section header with rounded top corners, titled Meters or Meter <UUID>. Compact
admin-only My/All tabs share the list header; the active tab is white with dark
text and joins the content. Names start read-only; pencil focuses editing and
changes to Save. Save/Enter persists, Escape cancels and errors retain drafts
on both pages. Name-only creation is the first list row; magnifier and clear-cross
controls are inside search. The shared theme uses 14px body/buttons, 18px headings
and 20px forecast values in rem, smaller fields/record buttons and no forced
uppercase; the account icon stays 42px. The list uses /meters, legacy / and
/meters/ entries canonicalise, and meter-ID reload/login/Back/Forward work.
Fourteen grouped live checks, all 31 frontend checks and the asset build passed.
Vite reports a non-blocking 534kB chunk-size warning; optimisation is not added
to this PoC task. Both demo ledgers are unchanged; no ledger writes or reminder
requests occurred. Disposable auth/meter/mail fixtures were cleaned up.
Backend, SQL, ownership/admin policy and forecast math are unchanged; refocus.md
is untouched. The user subsequently authorised the Git handoff of Tasks 037–041.
Task 042 updates the roadmap and component requirements only. New tickets are
65 usability, 66 synthetic forecasting validation, 67 external testing and
68 a future installable web app. Reuse 56 for personal usage validation, 57 for
web deployment and 58 for the supplied Monitor logo/modest Roventics credit.
Order: 65 -> 66 -> 57 -> begin 56 and 67; real household evidence follows
deployment rather than being its prerequisite. Task 042 originally deferred
logo placement; Task 043's approved identity delivery below completes it. PWA 68 waits for
web-usage evidence; React Native/mobile stores remain deferred.

The current schema stores balance/top-up kWh and UTC times, not purchase costs.
Costs, tariffs and future-price estimates stay deferred. Validation must explain
30-day usage versus additional kWh to buy: at 15 kWh/day and 300 kWh remaining,
usage is 450 kWh for 30 days, while the extra purchase is 150 kWh. Synthetic
demo/screenshot records are not real-household validation evidence.

While waiting for Monitor feedback, Switch 84 proceeds through compact
low-voltage assembly, a measured temporary enclosure and at least two continuous
weeks of internal tests; 85 replaces it after manufactured PCB arrival/bring-up.
SPII/supplier processes stay parallel. Task 042 changed no product, database,
infrastructure or hardware and approved none of those future implementations.
Task 043 completes Ticket 58: unchanged supplied monitor-logo.png appears as a
48px logo/name header above login and the workspace and as the PNG favicon.
The page title is Monitor. Shared MUI colours are blue #005aae, readable teal
#007782, white and pale blue #eef7fc, with dark blue-grey text. Rounded section
headers/forecast cards are blue; active admin tabs stay white with blue text.
Top-up/Refresh and the footer use teal. A 24px existing Roventics logo plus
by Roventics links to https://roventics.com in a separate safe new tab.
Fonts, 42px account icon, layout/flows, routes, permissions and forecasts are
unchanged. All 31 frontend checks and the production asset build passed, as did
four grouped browser checks covering 18 desktop/phone views using mocked APIs
on a disposable built-assets preview. No real backend request or DB write
occurred; source artwork hashes are unchanged. Temporary browser/server closed.
The user authorised the Git handoff of completed Tasks 043–044.
Task 044 refines the brand header:
the 48px logo sits above Monitor in one combined centred block, with Back left
and the 42px account control right, vertically centred against the whole block.
They share one compact row; phones below 600px show the account icon only and
retain the full email in its existing Sign out dropdown. Desktop email truncates
without shifting the centred branding. Login/loading keep the stacked identity
without navigation actions. Artwork, palette, fonts, routes, auth/permissions,
forecast logic and data are unchanged. Tasks 043–044 were committed and pushed
to master as eb08605; full Ticket 65 remains open.
Task 044 passed all 32 frontend checks, the TypeScript/Vite build and four
grouped mocked-browser checks across 16 desktop/phone views, including long
emails, Back, Sign out and Escape/focus restoration. No real backend requests
or DB writes occurred; the disposable browser/server closed after verification.

Task 045 is complete with small visual refinements only: Segoe UI /
system sans-serif fallbacks, unchanged 14/18/20px scale, consistent weights and
tabular estimate digits. The blue/teal identity and combined navigation remain.
Cards have subtle borders/shadows; details/list panels use 12px corners, inputs
10px and forecasts 16px. Light-blue hover/focus, a pale-teal creation row and a
blue/deep-teal forecast blend add restrained colour variation; a divider separates
monthly purchase output. Button/icon-button keyboard focus is explicit. No
wording, flow, backend, forecast/data, dependency or artwork changes. Task 046's
approved open layout below supersedes those card/surface choices; full usability
Ticket 65 is still a separate open review.
All 32 frontend checks, the TypeScript/Vite build and four grouped mocked-browser
checks across 20 desktop/phone views passed, including both forms, forecast
states, keyboard focus and representative contrast checks. No real backend/DB
request or write occurred; browser/server closed. See the Git handoff below.

Task 046 implements the approved card-free direction for login and the signed-in
workspace. A white page, slim blue headings, underlined admin tabs and flat
details/list rows replace enclosing cards and filled headers. Forecast values
appear directly on the page: blue balance/days, teal monthly recommendation,
muted labels and divider lines; no coloured forecast box. Figures stack below
600px, use two columns with monthly output beneath at 600–899px and three columns
at 900px+. The latest actual/calculation times, two record actions, on-demand
forms and collapsed History remain. Retains Task 045's fonts, numeric alignment,
input corners and focus styling. No wording, handler, calculation, backend,
data, permission, route, artwork or dependency changes. Task 047 follows below;
full Ticket 65 remains open. See the Git handoff below.
Task 046 passed all 32 frontend checks, the TypeScript/Vite build and four
grouped mocked-browser checks with 39 captures across phone/tablet/desktop
widths. Text contrast is at least 5.30:1 and input outlines 4.05:1 in representative
checks. No real backend/DB request, write or browser error; browser/server closed.

Task 047 implements conditional header search: visible only above 10 unfiltered
meters in the selected view, or while a query/filter is active. Centred between
Meters and My/All from 600px; its own header row on phones; absent on details.
The applied query is separate from its draft, so clearing typed text or getting
zero results cannot hide recovery. Full reads refresh the count; create/delete
update it and My/All clears/reloads. Account/list generations guard late replies,
including write follow-up reads. The existing server q search and permissions
are unchanged; no client keyword matching or pagination. At the user's follow-up
request, visible rows have one-based display numbers, reset per current result
list; UUIDs/names/data are untouched. Useful 045/046 styling is preserved.
Task 048 follows below; full Ticket 65 is still open.
Task 047 passed all 33 frontend checks and the TypeScript/Vite build. Its
145-line implementation records a necessary review-size exception in prompt.md
for relocating the field plus count/query/reply guards and requested numbering.
Five grouped mocked-browser checks and 25 phone/tablet/desktop captures passed:
thresholds, query/clear/failed-read recovery, My/All and CRUD crossings, numbering,
pending controls and delayed old-query/new-account reset. No real API/DB writes
or browser errors; isolated browser/server closed. See the Git handoff below.

Task 048 replaces the account icon/dropdown with a direct red Sign out button
at the top right on all devices, beside the email with a 4px gap. Emails truncate
on narrow screens while retaining their full text/title. The stacked 48px Monitor
logo/name stays centred, with Back on the left. Existing logout/Back handlers and
pending guards are unchanged; unused menu state/imports are removed. The footer's
by Roventics text is black; its 24px company logo and safe external link remain.
No other layout, artwork, backend, data, permission, route or dependency changes.
All 33 frontend checks and the TypeScript/Vite build passed, plus two focused
mocked-browser groups with 15 phone/tablet/desktop captures, including long email,
keyboard focus, Back, pending controls and sign-out failure/retry/success.
Red/white button contrast is 4.98:1. No real API/DB writes or browser errors;
the isolated browser/preview are closed.
Tasks 045–048 were committed and pushed to master as 301f50f.
Full Ticket 65 remains open. Current priority is
65 -> 66 -> 57 -> personal 56 and external 67; installable-app 68 remains future.

Task 049 adds the existing MUI Logout icon beside the red Sign out text on all
screens, distinct from Back. Compact icon spacing and narrower phone padding
retain email space; additional truncation is approved. Branding, handlers,
busy guards and all other layout/behaviour remain unchanged. All 33 frontend
checks and the TypeScript/Vite build passed. Two mocked-browser groups with
eight phone/tablet/desktop captures also passed,
including long-email truncation, distinct Back, pending controls and direct
logout. No real API/DB writes or browser errors; isolated browser/preview closed.
The user subsequently authorised committing and pushing Task 049 to master.
Next work number is 050; full usability Ticket 65 remains open.

After login, the active product flow is a list of the user's nickname-only
software meter profiles. Selecting one meter provides balance and purchased-kWh
entry actions, factual history, estimated current balance/days/run-out, and a
30-day kWh purchase recommendation. The UI shows `Not enough data` or
`Inconsistent history` rather than fabricating unavailable estimates.

Forecasting uses one reviewed deterministic method for every meter and
recalculates from that meter's history whenever a new point is added. All callers
use the single replaceable model function so a later evidence-backed method does
not require API/UI rewrites. History improves the estimate incrementally, but
this is not reinforcement learning or ML. A new meter has no guessed usage
baseline and must show `Not enough data` until real readings support the
calculation.

Development Compose reads its explicit values from the ignored `software/.env`.
The committed `.env.example` contains only safe local examples; personal admin
emails and secrets must remain untracked.

The root README owns stable ticket IDs and the current execution order. Ticket
48 performs an explicit active-code/domain cleanup before authentication and
feature tickets proceed.

## Deferred research

Hardware, firmware, camera capture, OCR, device upload, MQTT, anomaly ML and
meter interfaces are preserved but deferred. Revisit automation only if real
users find manual entry too inconvenient. Desktop OCR tests are never hardware
validation, and uncertain OCR must never become a trusted balance silently.

Automated top-ups, payment integration, tariffs, Rand forecasts, SMS, push
notifications, municipal dashboards and postpaid billing are also deferred.
Any future payment path requires authorised providers, consent, auditability and
explicit failure handling.

Any future physical meter work must remain external and non-invasive. Never
open, electrically modify, bypass or interfere with an installed meter.
Anomalies are investigation signals, not proof of theft or tampering.

## UI and brand references

The user has authorised read-only inspection of `../switch/hardware/web/` for
mobile interaction inspiration and `../roventics/frontend/images/` or
`../switch/assets/branding/roventics/` for future company artwork. Monitor UI
must remain a native React/Material UI implementation. Never modify sibling
repositories without a separate explicit request.

## Documentation rules

Use the nearest README; do not create a `docs/` directory. Keep root roadmap
summaries short and detailed requirements in component READMEs. Work records use
sequential three-digit directories. Do not commit secrets, private bills,
customer data, meter photographs or local database contents.
