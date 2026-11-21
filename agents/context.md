# Monitor context

## Current system

Prepaid-electricity planner. Source now has a local-only `/guest` workspace for one
meter, with the existing forecast/ledger UI. Task 092 is not deployed; the owner
reports the earlier email-login deployment working. Account access uses email OTP.
Users record balance/top-up kWh and occurrence times.
Named meters can be shared; members and DB `users.type=admin` have full access
within their scope. Open signup creates regular users; roles never come from
email/environment. Fresh seeds create the approved admin in both modes and
fictional meters only in development. Existing volumes never replay seeds.

React/Vite/Material UI; FastAPI, Psycopg and PostgreSQL with pure SQL.
Backend: `software/backend/app/{endpoints,modules,schemas}`.
Frontend: `software/frontend/src/{routes,components,lib}`.
Store UTC; input/display uses local time. One actual balance uses a labelled
10 kWh/day starting rate; valid intervals supply per-meter measured use.
No balance/inconsistent history stays unavailable. Show current balance,
remaining days/run-out, additional top-up and total monthly requirement.
Plan for strictly-next UTC 1st using the actual target month's length.

Opaque cookie sessions store only digests; current new-session lifetime is
30 days. Preserve OTP limits, server expiry/logout revocation, origin checks
and live role/member authorization. Monthly email has durable recipient state;
only monthly planning is automated. Production activation remains explicit.

## Next work

68.1–68.3 implemented: `routes/guest/{GuestPage,localMeter,forecast}`,
versioned `monitor.guest.v1` browser data and integer-unit forecast parity. Guest
records never enter API requests. Blocked/full storage keeps in-memory records;
corrupt data and detected tab conflicts are preserved until explicit recovery.
Account sessions never enter the guest store. Browser saving is not permanent.
Entry: home introduces balance, run-out and monthly purchase estimates with a
light-blue introduction, teal icons and one Log in action; `/login` offers
email or guest with an “or” divider. The app uses Monitor branding. Guest pages
omit routine storage/login-to-save copy; genuine failure warnings remain.
Next 68.4: the chosen account-saving flow, saving existing local history
after successful OTP without a separate copy screen. Retain originals, handle
retry/partial saves and hide the prompt after login. Ordinary login does not import.
68.6: unchecked-by-default Keep me signed in; checked lifetime is confirmed 3 days.
Existing runtime still uses 30-day sessions until this planned change is implemented.
Then 65 usability, 57.3 deploy and 67 recruitment/approximately 30-day feedback.
Native/PWA 68.5, research 66, hardware/OCR/ML, tariffs and payments stay later.

## Operations

One ignored `software/.env`, one safe example, exactly dev/prod Compose files.
Development uses localhost/Mailpit overrides. Production serves internal HTTP80
as `monitor-frontend` on external `roventics_proxy`; public HTTPS is upstream.
Backend/database are private; no production Mailpit. See `software/nginx/README.md`.
Preserve working routing, live data, backups, `refocus.md` and unique research.
Task 092 verified: build, 44 existing checks, 215 Python/browser forecast cases and
9 isolated browser groups. No source services, live data or deployment changed.
Entry refinements are recorded in Tasks 093–095. Task 095's build, 44 existing
checks and 1280/390/320px walkthrough pass. Root README owns priorities;
component READMEs own detail. Task 096 removes the company footer and prepares
the beta handoff. The user approved Git publication on 3 November 2026;
VPS rollout is the next operator step.
Task 097 restores the original company logo credit and improves homepage canonical
and nonpublic noindex headers, without changing account flows or landing copy.
Task 098 plans market-research Tickets 71.1–71.11 under
`software/research/market-research/`. Build only separately approved slices:
resumable link-graph/document discovery, factual context, required local LM Studio, validation,
then one restartable private contacts CSV. Stop after 71.7 for review; survey,
drafts, domain readiness and manually approved sending stay later. Inputs and
generated files remain inside that experiment and are ignored by default.
LM Studio is already installed; outages leave enrichment pending, preserving raw
data. Traverse all discovered in-scope links with cycle detection and retained
queues at limits; record unsupported formats rather than claiming they were read.
Task 099 / 71.1 implements offline --init/--check in one standard-library
pipeline.py. Private folders exist; the owner's links.txt is the default and
has 16 syntax-valid entries, preserved byte-for-byte. The owner requests small Qwen (~1.3B) for
71.5; confirm its actual identifier then. Existing forecasting stays in place.
Research plan/workspace published on master as 1b233b4 at the user's request.
Task 100 / 71.2 adds --crawl/--resume in the same standard-library script:
seed hosts/www initially, explicit extra hosts, deduplicated graph/parent links,
retained deferred branches, bounded requests, private atomic state/evidence and
a single writer. Public-IP pinning, TLS verification, robots rules and persisted
rate waits apply. No document reader, final CSV or model call yet.
Isolated checks pass. The approved five-attempt smoke fetched one HTML page:
76 discovered, 72 pending, three robots-access failures recorded. Private state
is at data/crawl_state.json and seed bytes are preserved. No full crawl was run.
Only four of 16 seeds were attempted (one fetched, three robots-stage failures);
12 seeds are request-budget pending, not known failures. Root causes are unverified.
Private per-seed review: data/task100-access-review.json. Next is 71.2.1 access
diagnostics before 71.3 readers; the next prompt is 101.
