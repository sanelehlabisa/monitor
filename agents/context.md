# Monitor context

## Current system

Deployed prepaid-electricity planner; owner reports it working. Runtime currently
requires email OTP login. Users record balance/top-up kWh and occurrence times.
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

68: local guest estimates/history without login. Accounts are optional for
account storage, recovery and another device; browser saving cannot guarantee
recovery after clearing/loss. Preserve existing accounts; keep guest records local.
68.1: one small meter/ledger storage boundary; 68.2: local calculation parity;
68.3: local workspace; 68.4: verified-session storage routing and optional login.
Homepage: Use without logging in. Guests: local writes and a Log in and save to
account prompt; hide it after login. Signed-in writes use the existing backend.
That explicit flow saves the existing guest meter/history after successful OTP;
there is no separate post-login copy screen. Retain local originals, report save
failures and prevent duplicate retries. Ordinary login does not silently import data.
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
Root README owns priorities; component READMEs own detail. Next work number: 092.
